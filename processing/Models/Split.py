from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd


def TestTrainSplit(file_name, features, label, ratio):

    dataset = pd.read_csv(file_name)
    X = dataset[features].values
    y = dataset[label].values
    sc= StandardScaler()
    X = sc.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = ratio, random_state = 0)

    return X, y, X_train, X_test, y_train, y_test
