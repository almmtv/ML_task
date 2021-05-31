import urllib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import ElasticNetCV
from sklearn.metrics import explained_variance_score
from sklearn.metrics import max_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import median_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_poisson_deviance



# date format: UNIX timestamp
def stock_candles(stock_name, date_from, date_to, api_key):
    link = 'https://finnhub.io/api/v1/stock/candle?symbol=' + stock_name + '&format=csv&resolution=D&from=' + date_from\
           + '&to=' + date_to + '&token=' + api_key
    try:
        candles = pd.read_csv(link, delimiter=',')
    except urllib.error.URLError:
        print('Connection error or Wrong token')
        candles = pd.DataFrame()
    return candles


# model training
def predict(regress, predictors_train, responses_train, predictors_test):
    reg = regress.fit(predictors_train, responses_train)
    responses_test = reg.predict(predictors_test)
    return responses_test


# the orange dots represent the prediction, the blue dots represent the actual value
def visualization(x_values, y_values1, y_values2, model_name):
    plt.scatter(x_values, y_values1)
    plt.scatter(x_values, y_values2)
    plt.title(model_name)
    plt.show()


def metrics(y_true, y_pred):
    list_of_metrics = [explained_variance_score, max_error, mean_squared_error,
                       median_absolute_error, mean_absolute_percentage_error, mean_poisson_deviance]
    res = []
    for metric in list_of_metrics:
        res.append(metric(y_true, y_pred))
    return res


stock = 'AMZN'
token = 'c240262ad3iaqj3tjgng'
data = stock_candles(stock, '1585699200', '1617235200', token)
data['mean'] = (data['h'] + data['l'])/2
data.drop(['h', 'l'], axis=1, inplace=True)
X = data['t']
Y = data['mean']
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=20)
x_train = np.array(x_train).reshape(-1, 1)
x_test = np.array(x_test).reshape(-1, 1)
y_train = np.array(y_train).reshape(-1)
y_test = np.array(y_test)
models = [LinearRegression(), DecisionTreeRegressor(), RandomForestRegressor(), ElasticNetCV(), SVR()]
predictions = []
results = {}
for model in models:
    predictions.append([predict(model, x_train, y_train, x_test), str(model)[:-2]])
for prediction in predictions:
    visualization(x_test, y_test, prediction[0], prediction[1])
    results[prediction[1]] = metrics(y_test, prediction[0])
for result in results:
    print(result, results[result])

