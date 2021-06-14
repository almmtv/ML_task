import queue
from threading import Thread
import datetime
import urllib
import psycopg2
import petl as etl
import sys
from flask import Flask, request, jsonify


class Database:
    def __init__(self, db_name, user_name, password):
        self.db_name = db_name
        self.user_name = user_name
        self.password = password
        self.con = psycopg2.connect(
            database=self.db_name,
            user=self.user_name,
            password=self.password,
            host='localhost',
            port='5432'
        )
        self.cursor = self.con.cursor()

    def disconnect(self):
        self.con.close()


def financial_quote_link(stock_name, api_key):
    link = 'https://finnhub.io/api/v1/quote?symbol=' + stock_name + '&token=' + api_key
    return link


def news_sentiment_link(stock_name, api_key):
    link = 'https://finnhub.io/api/v1/news-sentiment?symbol=' + stock_name + '&token=' + api_key
    return link


def basic_financials_link(stock_name, api_key, metric='all'):
    link = 'https://finnhub.io/api/v1/stock/metric?symbol=' + stock_name + '&metric=' + metric + '&token=' + api_key
    return link


# date format: YYYY-MM-DD
def insiders_transaction_link(stock_name, date_from, date_to, api_key):
    link = 'https://finnhub.io/api/v1/stock/insider-transactions?symbol=' + stock_name + '&from=' + date_from + \
           '&to=' + date_to + '&token=' + api_key
    return link


def recommendation_trends_link(stock_name, api_key):
    link = 'https://finnhub.io/api/v1/stock/recommendation?symbol=' + stock_name + '&token=' + api_key
    return link


def url_request(url):
    table_header = url[url.find('v1') + 3:url.find('?')]
    try:
        r = etl.fromtext(url, header=[table_header])
    except urllib.error.URLError:
        print('Connection error or Wrong token')
        r = ''
    return r


stock = sys.argv[-1]
token = 'c240262ad3iaqj3tjgng'
links = [financial_quote_link(stock, token), news_sentiment_link(stock, token), basic_financials_link(stock, token),
         insiders_transaction_link(stock, '2021-02-03', '2021-05-03', token), recommendation_trends_link(stock, token)]

que = queue.Queue()
threads_list = list()
for link in links:
    t = Thread(target=lambda q, arg1: q.put(url_request(arg1)), args=(que, link))
    t.start()
    threads_list.append(t)
for t in threads_list:
    t.join()
result = []
while not que.empty():
    result.append(que.get())

price = []
recommendation = []
insiders = []
metrics = []
sentiment = []
for value in result:
    table_h = value[0][0]
    table_c = eval(value[1][0].replace('null', 'None'))
    if table_h == 'quote':
        table_c['t'] = str(datetime.datetime.fromtimestamp(table_c['t']))
        price = table_c
    if table_h == 'stock/insider-transactions':
        for transaction in table_c['data']:
            insiders.append(transaction)
    if table_h == 'news-sentiment':
        sentiment = table_c
    if table_h == 'stock/recommendation':
        for recommend in table_c:
            recommendation.append(recommend)
    if table_h == 'stock/metric':
        metrics = table_c['metric']

table_price = etl.fromdicts([price])
table_price = etl.addfield(table_price, 'symbol', stock)
table_recommendation = etl.movefield(etl.fromdicts(recommendation), 'period', 6)
table_insiders = etl.movefield(etl.fromdicts(insiders), 'transactionDate', 6)
table_insiders = etl.addfield(table_insiders, 'symbol', stock)

list_of_metrics = ['10DayAverageTradingVolume', '13WeekPriceReturnDaily', '26WeekPriceReturnDaily',
                   '3MonthAverageTradingVolume', '52WeekHigh', '52WeekHighDate', '52WeekLow', '52WeekLowDate',
                   '52WeekPriceReturnDaily', '5DayPriceReturnDaily']
important_metrics = {}
for metric in list_of_metrics:
    important_metrics[metric] = metrics[metric]
important_metrics['_date'] = str(datetime.datetime.now())[:19]
table_metrics = etl.fromdicts([important_metrics])
table_financial_metrics = etl.rename(table_metrics, {'10DayAverageTradingVolume': '_10DayAverageTradingVolume',
                                                     '13WeekPriceReturnDaily': '_13WeekPriceReturnDaily',
                                                     '26WeekPriceReturnDaily': '_26WeekPriceReturnDaily',
                                                     '3MonthAverageTradingVolume': '_3MonthAverageTradingVolume',
                                                     '52WeekHigh': '_52WeekHigh',
                                                     '52WeekHighDate': '_52WeekHighDate',
                                                     '52WeekLow': '_52WeekLow',
                                                     '52WeekLowDate': '_52WeekLowDate',
                                                     '52WeekPriceReturnDaily': '_52WeekPriceReturnDaily',
                                                     '5DayPriceReturnDaily': '_5DayPriceReturnDaily'})
table_financial_metrics = etl.addfield(table_financial_metrics, 'symbol', stock)

list_of_sentiments = ['bearishPercent', 'bullishPercent']
important_sentiments = {}
for sentiments in list_of_sentiments:
    important_sentiments[sentiments] = sentiment['sentiment'][sentiments]
important_sentiments['date_and_time'] = str(datetime.datetime.now())[:19]
table_sentiment = etl.fromdicts([important_sentiments])
table_sentiment = etl.addfield(table_sentiment, 'symbol', stock)
tables_without_symbol = [table_price, table_insiders, table_financial_metrics, table_sentiment]

db = Database('postgres', 'postgres', '123456f')
db_connection = db.con
etl.appenddb(table_price, db_connection, 'price')
etl.todb(table_recommendation, db_connection, 'recommendation')
etl.todb(table_insiders, db_connection, 'insiders')
etl.appenddb(table_financial_metrics, db_connection, 'financial_metrics')
etl.appenddb(table_sentiment, db_connection, 'sentiment')

# data for first request
db.cursor.execute('select NAME from INSIDERS')
data1 = db.cursor.fetchall()
data1 = list(set(data1))

# data for second request
db.cursor.execute('select * from INSIDERS')
data2 = db.cursor.fetchall()
data2_modify = {}
for row in data2:
    if row[0] not in data2_modify:
        data2_modify[row[0]] = []
    data2_modify[row[0]] += [row[1:]]
data2 = data2_modify

# data for third request
db.cursor.execute('select buy, period from recommendation')
data3 = db.cursor.fetchall()
data3_modify = {}
for row in data3:
    data3_modify[row[1]] = row[0]
data3 = data3_modify
db.disconnect()


app = Flask(__name__)


@app.route('/')
def hello():
    return 'HELLO!'


# returns the names of all insiders
@app.route('/insider_names/', methods=['GET', 'POST'])
def ins_name_list():
    if request.method == 'POST':
        return 'post requests are not processed'
    else:
        response = jsonify(data1)
        response.status_code = 200
        return response


# returns information about the insider by name
@app.route('/insider_info/', methods=['GET', 'POST'])
def ins_info():
    if request.method == 'POST':
        return 'post requests are not processed'
    else:
        response = jsonify(list(data2[request.args.get('insider_name')]))
        response.status_code = 200
        return response


# returns a buy recommendation for a specific date
@app.route('/sentiment/', methods=['GET', 'POST'])
def recommendation_to_buy():
    if request.method == 'POST':
        return 'post requests are not processed'
    else:
        response = str(data3[request.args.get('date')])
        return response
