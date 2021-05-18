import requests
import queue
from threading import Thread
import datetime
import psycopg2
import sys


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

    def connect(self):
        pass

    def disconnect(self):
        self.con.commit()
        self.con.close()

    def insert(self, table_name, values):
        self.cursor.execute(
            f"INSERT INTO {table_name} VALUES {values}"
        )


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


def request(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('Connection error')
        return None
    if str(r) == '<Response [401]>':
        print('Wrong token')
        return None
    return r.json()


stock = sys.argv
token = 'c240262ad3iaqj3tjgng'
links = [financial_quote_link(stock, token), news_sentiment_link(stock, token), basic_financials_link(stock, token),
         insiders_transaction_link(stock, '2021-02-03', '2021-05-03', token), recommendation_trends_link(stock, token)]

que = queue.Queue()
threads_list = list()
for link in links:
    t = Thread(target=lambda q, arg1: q.put(request(arg1)), args=(que, link))
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
    print(value)
    if 'c' in value:
        value['t'] = str(datetime.datetime.fromtimestamp(value['t']))
        price = value
    if 'data' in value:
        for transaction in value['data']:
            insiders.append(transaction)
    if 'metric' in value:
        metrics = value['metric']
    if 'buzz' in value:
        sentiment = value
    if (len(value) > 1) and ('buy' in value):
        for j in value:
            recommendation.append(j)

price_for_table = []
recommendation_for_table = []
insiders_for_table = []
metrics_for_table = []
sentiment_for_table = []

for value in price:
    if value != 't':
        price_for_table.append(float(price[value]))
price_for_table.append(price['t'])
price = tuple(price_for_table)

for i in range(len(recommendation)):
    recommendation_for_table.append([])
    for value in recommendation[i]:
        if (value != 'period') and (value != 'symbol'):
            recommendation_for_table[i].append(recommendation[i][value])
    recommendation_for_table[i].append(recommendation[i]['period'])
    recommendation_for_table[i] = tuple(recommendation_for_table[i])

for i in range(len(insiders)):
    insiders_for_table.append([])
    for metric in insiders[i]:
        if metric != 'transactionDate':
            insiders_for_table[i].append((insiders[i][metric]))
    insiders_for_table[i].append(insiders[i]['transactionDate'])
    insiders_for_table[i] = tuple(insiders_for_table[i])

list_of_metrics = ['10DayAverageTradingVolume', '13WeekPriceReturnDaily', '26WeekPriceReturnDaily',
                   '3MonthAverageTradingVolume', '52WeekHigh', '52WeekHighDate', '52WeekLow', '52WeekLowDate',
                   '52WeekPriceReturnDaily', '5DayPriceReturnDaily']
for metric in list_of_metrics:
    metrics_for_table.append(metrics[metric])
metrics_for_table.append(str(datetime.datetime.now())[:19])
metrics = tuple(metrics_for_table)

list_of_sentiments = ['bearishPercent', 'bullishPercent']
for sentiments in list_of_sentiments:
    sentiment_for_table.append(sentiment['sentiment'][sentiments])
sentiment_for_table.append(str(datetime.datetime.now())[:19])
sentiment = tuple(sentiment_for_table)

# Creating tables
# db = Database('postgres', 'postgres', '123456f')
# db.connect()
# db.cursor.execute('''CREATE TABLE PRICE
#      (CURRENT_PRICE FLOAT,
#      HIGH_PRICE_OF_THE_DAY FLOAT,
#      LOW_PRICE_OF_THE_DAY FLOAT,
#      OPEN_PRICE_OF_THE_DAY FLOAT,
#      PREVIOUS_CLOSE_PRICE FLOAT,
#      DATE_AND_TIME CHAR(19));''')
# db.cursor.execute(''' CREATE TABLE RECOMMENDATION
#     (BUY INT,
#     HOLD INT,
#     SELL INT,
#     STRONG_BUY INT,
#     STRONG_SELL INT,
#     PERIOD CHAR(10));''')
# db.cursor.execute(''' CREATE TABLE INSIDERS
#     (INSIDER_NAME VARCHAR(50),
#     SHARE INT,
#     CHANGE INT,
#     FILING_DATE VARCHAR(10),
#     TRANSACTION_CODE VARCHAR(2),
#     TRANSACTION_PRICE FLOAT,
#     TRANSACTION_DATE VARCHAR(10));''')
# db.cursor.execute(''' CREATE TABLE FINANCIAL_METRICS
#     (_10_DAY_AVERAGE_TRAIDING_VOLUME FLOAT,
#     _13_WEEK_PRICE_RETURN_DAILY FLOAT,
#     _26_WEEK_PRICE_RETURN_DAILY FLOAT,
#     _3_MONTH_AVERAGE_TRAIDING_VOLUME FLOAT,
#     _52_WEEK_HIGH FLOAT,
#     _52_WEEK_HIGH_DATE CHAR(19),
#     _52_WEEK_LOW FLOAT,
#     _52_WEEK_LOW_DATE CHAR(19),
#     _52_WEEK_PRICE_RETURN_DAILY FLOAT,
#     _5_DAY_PRICE_RETURN_DAILY FLOAT,
#     DATE_AND_TIME CHAR(19));''')
# db.cursor.execute(''' CREATE TABLE SENTIMENT
#     (BEARISH_PERCENT FLOAT,
#     BULLISH_PERCENT FLOAT,
#     DATE_AND_TIME CHAR(19));''')
# disconnect(connection)

# Writing to a table
# db = Database('postgres', 'postgres', '123456f')
# db.connect()
# db.insert('PRICE', price)
# for recommend in recommendation_for_table:
#     db.insert('RECOMMENDATION', recommend)
# for insiders in insiders_for_table:
#     db.insert('RECOMMENDATION', recommend)
# db.insert('FINANCIAL_METRICS', metrics)
# db.insert('SENTIMENT', sentiment)
# db.disconnect()
