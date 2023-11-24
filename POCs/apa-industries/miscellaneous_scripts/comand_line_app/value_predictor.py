import os
import argparse
import time
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import numpy as np
from pandas import read_csv
from sklearn.preprocessing import LabelEncoder
from keras.models import load_model

# convert series to supervised learning
from config import Constant, Config
import tensorflow as tf
import pandas as pd

tf.get_logger().setLevel('ERROR')
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


class Predictor:

    def __init__(self):
        self.data_set = read_csv(Constant.DATA_PATH + 'outlier_removed.csv')

        self.model = load_model(
            './model/NO_OF_DAYS_epoch(1000)_lstm(300)_batch(512)_optimizer(adam)_loss(mae)_activation(relu)/')
        values = self.data_set.values
        # integer encode direction
        self.make_encoder = LabelEncoder()
        self.category_encoder = LabelEncoder()
        self.first_sold_encoder = LabelEncoder()
        sdate = datetime.strptime('1990-01-01', "%Y-%m-%d")
        edate = datetime.strptime('2022-12-31', "%Y-%m-%d")
        date_list = pd.date_range(sdate, edate, freq='d')
        date_list = [x.strftime('%Y-%m-%d') for x in date_list.to_list()]
        self.first_sold_encoder.fit(date_list)

        self.make_encoder.fit(values[:, 4])
        self.category_encoder.fit(values[:, 5])

    # print(reframed.head())
    def run(self, input):
        # input["firstSold"] = datetime.strptime(input["firstSold"], '%Y-%m-%d')
        # first_sold = time.mktime(input["firstSold"].date().timetuple())
        first_sold = self.first_sold_encoder.transform([input["firstSold"]])[0]
        make = self.make_encoder.transform([input["make"]])[0]
        cat = self.category_encoder.transform([input["category"]])[0]
        arr = np.array([(first_sold,
                         input["vehicleMaxQty"],
                         input["isDevelopment"],
                         make,
                         cat,
                         input["year"],
                         input["TotalVIO"],
                         input["no_of_days"],
                         input["HasPartsAuthorityPurchased"],
                         input["HasWorldPacPurchased"],
                         input["HasSSFPurchased"])])
        test_X = arr
        test_X.astype('int32')
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

        # make a prediction
        forecast = self.model.predict(test_X)
        forecast = forecast.astype('int32')
        print(forecast[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--firstSold', type=str, required=True)
    parser.add_argument('--vehicleMaxQty', type=int, required=True)
    parser.add_argument('--isDevelopment', type=int, required=True)
    parser.add_argument('--make', type=str, required=True)
    parser.add_argument('--category', type=str, required=True)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--TotalVIO', type=int, required=True)
    parser.add_argument('--no_of_days', type=int, required=False, default=365)
    parser.add_argument('--HasPartsAuthorityPurchased', type=int, required=True)
    parser.add_argument('--HasWorldPacPurchased', type=int, required=True)
    parser.add_argument('--HasSSFPurchased', type=int, required=True)
    args = parser.parse_args()
    o = Predictor()
    input = vars(args)
    o.run(input)
