import warnings
warnings.filterwarnings("ignore")
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import numpy as np
from pandas import read_csv
from sklearn.preprocessing import LabelEncoder
from keras.models import load_model

# convert series to supervised learning
from comand_line_app.config import Constant, Config
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


class Predictor:

    def __init__(self):
        self.data_set = read_csv(Constant.DATA_PATH + 'range_pre_processed_without_id.csv')
        self.model = load_model(
            './model/RANGE_Model_epoch(1000)_lstm(864)_batch(864)_optimizer(adam)_loss(mae)_activation(softmax)/')
        values = self.data_set.values
        # integer encode direction
        self.range_encoder = LabelEncoder()
        self.make_encoder = LabelEncoder()
        self.category_encoder = LabelEncoder()
        self.first_sold_encoder = LabelEncoder()

        self.range_encoder.fit(values[:, 0])
        self.first_sold_encoder.fit(values[:, 1])
        self.make_encoder.fit(values[:, 4])
        self.category_encoder.fit(values[:, 5])

    # print(reframed.head())
    def run(self, input):
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
                         input["SaleYearRank"],
                         input["HasPartsAuthorityPurchased"],
                         input["HasWorldPacPurchased"],
                         input["HasSSFPurchased"])])
        test_X = arr
        test_X.astype('int32')
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))

        # make a prediction
        forecast = self.model.predict(test_X)
        forecast = forecast.astype('int32')
        print(self.range_encoder.inverse_transform(forecast)[0])


if __name__ == "__main__":
    o = Predictor()
    input = {}
    input["firstSold"] = '2021-02-16 00:51:40.410'
    input["vehicleMaxQty"] = 1
    input["isDevelopment"] = 1
    input["make"] = "Volvo"
    input["category"] = "Fuel"
    input["year"] = 2021
    input["TotalVIO"] = 410632
    input["SaleYearRank"] = 1
    input["HasPartsAuthorityPurchased"] = 0
    input["HasWorldPacPurchased"] = 0
    input["HasSSFPurchased"] = 0
    o.run(input)

    input["firstSold"] = '2018-05-31 04:21:31.483'
    input["vehicleMaxQty"] = 1
    input["isDevelopment"] = 0
    input["make"] = "Chevrolet"
    input["category"] = "Cooling"
    input["year"] = 2020
    input["TotalVIO"] = 30716
    input["SaleYearRank"] = 3
    input["HasPartsAuthorityPurchased"] = 1
    input["HasWorldPacPurchased"] = 0
    input["HasSSFPurchased"] = 0
    o.run(input)