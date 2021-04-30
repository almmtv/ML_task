import requests
r = requests.get('https://finnhub.io/api/v1/quote?symbol=AMZN&token=c240262ad3iaqj3tjgng')
print('\n_____________Financial quote___________\n')
print('Current price:', r.json()['c'])
print('Open price of the day:', r.json()['o'])
print('High price of the day:', r.json()['h'])
print('Low price of the day:', r.json()['l'])
print('Previous close price:', r.json()['pc'])
print('\n______________COMPANY NEWS________________\n')
r = requests.get('https://finnhub.io/api/v1/company-news?symbol=AMZN&from=2021-04-28&to=2021-04-28&token=c240262ad3iaqj3tjgng')
for news in r.json():
    print('headline: ', news['headline'])
    print('summary: ', news['summary'])
    print('url: ', news['url'])
print('\n______________News Sentiment______________\n')
r = requests.get('https://finnhub.io/api/v1/news-sentiment?symbol=AMZN&token=c240262ad3iaqj3tjgng')
print('Sector Average Bullish Percent: ', r.json()['sectorAverageBullishPercent'])
print('Sector Average News Score: ', r.json()['sectorAverageNewsScore'])
print('Bearish percent: ', r.json()['sentiment']['bearishPercent'])
print('Bullish Percent: ', r.json()['sentiment']['bullishPercent'])
print('\n______________Basic Financials____________\n')
r = requests.get('https://finnhub.io/api/v1/stock/metric?symbol=AMZN&metric=all&token=c240262ad3iaqj3tjgng')
for metric in r.json()['metric']:
    print(metric, r.json()['metric'][metric])
print('\n______________Insiders Transaction________________\n')
r = requests.get('https://finnhub.io/api/v1/stock/insider-transactions?symbol=AMZN&from=2021-02-12&to=2021-04-27&token=c240262ad3iaqj3tjgng')
for operation in r.json()['data']:
    for detail in operation:
        print(detail, ': ', operation[detail])
    print('')
print('_________________Recommendation Trends____________\n')
r = requests.get('https://finnhub.io/api/v1/stock/recommendation?symbol=AMZN&token=c240262ad3iaqj3tjgng')
for recommendation in r.json()[0]:
    if recommendation != 'symbol':
        print(recommendation, r.json()[0][recommendation])