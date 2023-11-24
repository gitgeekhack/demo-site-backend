from math import sqrt

import numpy as np
from keras.models import load_model
from pandas import read_csv
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

# convert series to supervised learning
from model_training_app.config import Constant

# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], True)

model = load_model(
    'D:/machine-learning-experiments/apa-industries/model_training_app/model/data_update6/e(1000)_lstm(256)_b(1024)_o(adam)_l(mae)_a(relu)')


def get_mock_data(df):
    x = df[df['year'] == 2020].copy()
    # x = df[(df['year'] == 2020)
    #        & (df['vehicleMaxQty'] == 22)
    #        & (df['make'] == "BMW")].copy()
    x['year'] = 2021
    x = x.reset_index()
    x = x.drop("index", axis=1)
    units_360 = x["units_sold_360"].tolist()
    units_sold = x["units_sold"].tolist()
    x = x.drop("units_sold_360", axis=1)
    x['units_sold'] = np.nan
    x['sale_year_rank'] = x['sale_year_rank'] + 1
    return x, units_360, units_sold


# load dataset
dataset = read_csv(Constant.PREPROCESSED_WITHOUT_PART_ID_DATA_FILE)
mock_data, units_360, actul_sales = get_mock_data(dataset)
dataset = dataset.drop("units_sold_360", axis=1)
values = dataset.values

# integer encode direction
make_encoder = LabelEncoder()
category_encoder = LabelEncoder()
sub_category_encoder = LabelEncoder()
part_name_encoder = LabelEncoder()
scalar_x = StandardScaler()
scalar_y = StandardScaler()

part_name_encoder.fit(values[:, 1])
make_encoder.fit(values[:, 4])
category_encoder.fit(values[:, 5])
sub_category_encoder.fit(values[:, 6])

values[:, 1] = part_name_encoder.transform(values[:, 1])
values[:, 4] = make_encoder.transform(values[:, 4])
values[:, 5] = category_encoder.transform(values[:, 5])
values[:, 6] = sub_category_encoder.transform(values[:, 6])
scalar_x.fit(values[:, 1:])
scalar_y.fit(values[:, 0].reshape(len(values), 1))

values = mock_data.values

values[:, 1] = part_name_encoder.transform(values[:, 1])
values[:, 4] = make_encoder.transform(values[:, 4])
values[:, 5] = category_encoder.transform(values[:, 5])
values[:, 6] = sub_category_encoder.transform(values[:, 6])
# ensure all data is float

# values[:, 0] = scalar_y.transform(values[:, 0].reshape(len(values),1)).reshape(len(values))
values[:, 1:] = scalar_x.transform(values[:, 1:])
values = values.astype('float64')
# np.random.shuffle(values)
test = values

test_X, test_y = test[:, 1:], test[:, 0]

# reshape input to be 3D [samples, timesteps, features]

test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
# print(test_X.shape, test_y.shape)

# make a prediction
yhat = model.predict(test_X)
# inv_yhat = np.concatenate((yhat, test_X), axis=1)
inv_yhat = scalar_y.inverse_transform(yhat).reshape(len(yhat))
# inv_yhat = scaler.inverse_transform(inv_yhat)
forecast = inv_yhat
forecast = forecast.astype('int64')

rmse = sqrt(mean_squared_error(actul_sales, forecast))
print('Test RMSE: %.3f' % rmse)

# df = pd.DataFrame(columns=['Forecasted'], data=out)
mock_data['Forecasted'] = forecast
mock_data['units_sold'] = actul_sales
df = mock_data[['Forecasted', 'units_sold',
                "partType", "vehicleMaxQty",
                "isDevelopment", "make", "category", "subCat", "year",
                "TotalVIO", "HasPartsAuthorityPurchased",
                "HasWorldPacPurchased", "HasSSFPurchased", "sale_year_rank"]]
# df = pd.DataFrame(columns=['Forecasted', 'Actual'], data=out)

# df["Units Sold 360"] = units_360
df = df[['Forecasted', 'units_sold',
         "partType", "vehicleMaxQty",
         "isDevelopment", "make", "category", "subCat", "year",
         "TotalVIO", "HasPartsAuthorityPurchased",
         "HasWorldPacPurchased", "HasSSFPurchased", "sale_year_rank"]]
df['Forecasted'] = df['Forecasted'].apply(lambda x: abs(int(x)))
df['Diff With Actual'] = df['units_sold'] - df['Forecasted']
# df['Diff With Units Sold 360'] = df['Units Sold 360'] - df['Forecasted']
df['Variance'] = (df['units_sold'] - df['Forecasted']) / df['units_sold']
df['Actal Variance%'] = df['Variance'] * 100
# df['Variance'] = (df["Units Sold 360"] - df['Forecasted']) / df["Units Sold 360"]
# df['Units Sold 360 Variance%'] = df['Variance'] * 100
df = df.drop('Variance', axis=1)
df.to_csv('Validation_test_results.csv', index=False)
