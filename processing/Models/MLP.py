from math import sqrt
from numpy import array
from numpy import mean
from numpy import std
from pandas import DataFrame
from pandas import concat
from pandas import read_csv
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense
from matplotlib import pyplot
from django.shortcuts import render, redirect
# split a univariate dataset into train/test sets
def train_test_split(data, n_test):
  return data[:-n_test], data[-n_test:]

def series_to_supervised(data, n_in, n_out=1):
  df = DataFrame(data)
  cols = list()
  # input sequence (t-n, ... t-1)
  for i in range(n_in, 0, -1):
    cols.append(df.shift(i))
  # forecast sequence (t, t+1, ... t+n)
  for i in range(0, n_out):
    cols.append(df.shift(-i))
  # put it all together
  agg = concat(cols, axis=1)
  # drop rows with NaN values
  agg.dropna(inplace=True)
  return agg.values

# root mean squared error or rmse
def measure_rmse(actual, predicted):
  return sqrt(mean_squared_error(actual, predicted))

# fit a model
def model_fit(train, config):
  # unpack config
  n_input, n_nodes, n_epochs, n_batch = config
  # prepare data
  data = series_to_supervised(train, n_input)
  train_x, train_y = data[:, :-1], data[:, -1]
  # define model
  model = Sequential()
  model.add(Dense(n_nodes, activation='relu', input_dim=n_input))
  model.add(Dense(1))
  model.compile(loss='mse', optimizer='adam')
  # fit
  model.fit(train_x, train_y, epochs=n_epochs, batch_size=n_batch, verbose=0)
  return model

# forecast with a pre-fit model
def model_predict(model, history, config):
  # unpack config
  n_input, _, _, _ = config
  # prepare data
  x_input = array(history[-n_input:]).reshape(1, n_input)
  # forecast
  yhat = model.predict(x_input, verbose=0)
  return yhat[0]

# walk-forward validation for univariate data
def walk_forward_validation(data, n_test, cfg):
  predictions = list()
  # split dataset
  train, test = train_test_split(data, n_test)
  # fit model
  model = model_fit(train, cfg)
  # seed history with training dataset
  history = [x for x in train]
  # step over each time-step in the test set
  for i in range(len(test)):
  # fit model and make forecast for history
    yhat = model_predict(model, history, cfg)
    # store forecast in list of predictions
    predictions.append(yhat)
    # add actual observation to history for the next loop
    history.append(test[i])
  # estimate prediction error
  error = measure_rmse(test, predictions)
  # print(' > %.3f' % error)
  return error

# repeat evaluation of a config
def repeat_evaluate(data, config, n_test, n_repeats=30):
  # fit and evaluate the model n times
  scores = [walk_forward_validation(data, n_test, config) for _ in range(n_repeats)]
  return scores

# summarize model performance
def summarize_scores(name, scores):
  # print a summary
  scores_m, score_std = mean(scores), std(scores)
  # print('%s: %.3f RMSE (+/- %.3f)' % (name, scores_m, score_std))
  # box and whisker plot
  pyplot.boxplot(scores)
  #pyplot.show()
  return score_std

# series = read_csv('B2BForecast2.csv', header=0, index_col=0)
# data = series.values
# # data split
# n_test = 12
# # define config
# config = [24, 500, 100, 100]
# # grid search
# scores = repeat_evaluate(data, config, n_test)
# # summarize scores
# summarize_scores('mlp', scores)

# series_to_supervised(data, n_in=3, n_out=1)
# train = data[:-n_test]
# test = data[-n_test:]
# model_fit(train,config)
# walk_forward_validation(data, n_test, config)
# history = [x for x in train]
# model_predict(model_fit(train, config), history, config)

def MLP(request):
    if request.method == 'POST':
        try:
            file_name = request.POST['filename']
            my_file = "media/user_{0}/processed_csv/{1}".format(request.user, file_name)
            series = read_csv(my_file, header=0, index_col=0)
            # features = request.POST.getlist('features')
            # features_list = []
            # for feature in features:
            #     feature = feature[1:-1]
            #     feature = feature.strip().split(", ")
            #     for i in feature:
            #         features_list.append(i[1:-1])
            # label = request.POST['label']
            # ratio = request.POST['ratio']
            # -----------------------------------------------------------------------
            data = series.values
            # data split
            n_test = int(request.POST['ratio'])
            print(n_test)
            # define config
            config = [24, 500, 100, 100]
            print(1)
            # grid search
            scores = repeat_evaluate(data, config, n_test)
            print(2)
            # summarize scores
            score = summarize_scores('MLP', scores)
            print(3)

            series_to_supervised(data, n_in=3, n_out=1)
            print(4)
            train = data[:-n_test]
            test = data[-n_test:]
            model_fit(train,config)

            walk_forward_validation(data, n_test, config)
            print(5)
            history = [x for x in train]
            print(6)
            model_predict(model_fit(train, config), history, config)
            print(7)
            md = "MLP"
            return render(request, 'models/result.html', {"md": md,                      
                                                              "score": score})

        except Exception as e:
            return render(request, 'models/result.html', {"Error": e})