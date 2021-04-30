import requests
import pandas as pd
from pandas_profiling import ProfileReport

# данные о стоимости акции за каждый день с 1 апреля 2020 по 1 апреля 2021 (цена открытия, закрытия предыдущего дня,
# минимальная, максимальная и т.д.)
r = requests.get('https://finnhub.io/api/v1/stock/candle?symbol=AMZN&format=csv&resolution=D&from=1585699200&to'
                 '=1617235200&token=c240262ad3iaqj3tjgng')
# запись в файл data.csv
with open('data.csv', 'w') as f:
    f.write(r.content.decode('utf-8'))
data = pd.read_csv('data.csv', delimiter=',', index_col='t')
# анализ данных и его запись в файл report.html
profile = ProfileReport(data, title='Pandas Profiling Report', explorative=True)
profile.to_file("report.html")