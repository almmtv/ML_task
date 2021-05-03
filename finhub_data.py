import requests
from multiprocessing.pool import ThreadPool
import sys


def financial_quote_link(stock_name, api_key):
    link = 'https://finnhub.io/api/v1/quote?symbol=' + stock_name + '&token=' + api_key
    return link


# date format: YYYY-MM-DD
def company_news_link(stock_name, date_from, date_to, api_key):
    link = 'https://finnhub.io/api/v1/company-news?symbol=' + stock_name + '&from=' + date_from + '&to=' + date_to + \
           '&token=' + api_key
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


def request(link):
    try:
        r = requests.get(link)
    except requests.exceptions.ConnectionError:
        print('Connection error')
        return None
    if str(r) == '<Response [401]>':
        print('Wrong token')
        return None
    return r.json()


stock = sys.argv[-1]
token = 'c240262ad3iaqj3tjgng'
links = [financial_quote_link(stock, token), company_news_link(stock, '2021-05-02', '2021-05-03', token),
         news_sentiment_link(stock, token), basic_financials_link(stock, token),
         insiders_transaction_link(stock, '2021-02-03', '2021-05-03', token), recommendation_trends_link(stock, token)]
pool = ThreadPool(8)
results = pool.map(request, links)
pool.close()
pool.join()
