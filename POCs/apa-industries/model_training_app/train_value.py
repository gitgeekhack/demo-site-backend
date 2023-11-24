import os
from datetime import datetime
from math import sqrt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import tensorflow
import numpy as np
import matplotlib

matplotlib.use('Agg')  # changed the backend

from matplotlib import pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, Dropout, Bidirectional
from keras.layers import LSTM
from model_training_app.config import Constant, Config
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.python.keras import backend as K

# adjust values to your needs
# config = tensorflow.compat.v1.ConfigProto(device_count={'GPU': 0})
config = tensorflow.compat.v1.ConfigProto(device_count={'GPU': 1, 'CPU': 1})
config.gpu_options.allow_growth = True
sess = tensorflow.compat.v1.Session(config=config)
K.set_session(sess)
tensorflow.compat.v1.logging.set_verbosity(tensorflow.compat.v1.logging.ERROR)


def soft_acc(y_true, y_pred):
    return K.mean(K.equal(K.round(y_true), K.round(y_pred)))


class TrainModelWithValue:
    #
    # def mean_absolute_percentage_error(self, y_true, y_pred):
    #     # y_true, y_pred = np.array(y_true), np.array(y_pred)
    #     return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    def save_stats(self, epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval, rmse):
        try:
            x = pd.read_csv('stats.csv')
        except Exception as e:
            x = pd.DataFrame()
        df = pd.DataFrame(
            columns=["epoch", "lstm_nodes", "batch", "optimizer", "loss_eval", "RMSE", "MAPE", "at"],
            data=[
                [epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval, rmse, None, datetime.now().isoformat()]])
        x = pd.concat([x, df])
        x.to_csv('stats.csv', index=False)

    def run(self, epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval, activation_var):
        from tqdm.keras import TqdmCallback

        my_callbacks = [
            TqdmCallback(verbose=0),
            tensorflow.keras.callbacks.TensorBoard(
                log_dir=Constant.LOG_BASE_PATH.format(epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval,
                                                      activation_var.__name__ if activation_var else None)),
        ]
        dataset = pd.read_csv(Constant.PREPROCESSED_WITHOUT_PART_ID_DATA_FILE)
        dataset = dataset.drop("units_sold_360", axis=1)
        dataset = dataset[dataset['year'] <= 2020]
        # dataset = dataset[:len(dataset) - int((len(dataset) / 10))]
        values = dataset.values
        # np.random.shuffle(values)
        scaler_x = StandardScaler()
        scaler_y = StandardScaler()
        # integer encode direction
        make_encoder = LabelEncoder()
        category_encoder = LabelEncoder()
        sub_category_encoder = LabelEncoder()
        part_name_encoder = LabelEncoder()

        values[:, 1] = part_name_encoder.fit_transform(values[:, 1])
        values[:, 4] = make_encoder.fit_transform(values[:, 4])
        values[:, 5] = category_encoder.fit_transform(values[:, 5])
        values[:, 6] = sub_category_encoder.fit_transform(values[:, 6])
        # ensure all data is float
        values[:, 0] = scaler_y.fit_transform(values[:, 0].reshape(len(values),1)).reshape(len(values))
        values[:, 1:] = scaler_x.fit_transform(values[:, 1:])

        values = values.astype('float64')

        np.random.shuffle(values)
        test, train = np.split(values, [int(Config.TEST_DATA_SPLIT_RATIO * len(values))])

        train_X, train_y = train[:, 1:], train[:, 0]
        test_X, test_y = test[:, 1:], test[:, 0]
        # reshape input to be 3D [samples, timesteps, features]
        train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
        # print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

        # design network
        with tensorflow.device("/device:GPU:0"):
            # with tensorflow.device('/cpu:0'):
            model = Sequential()
            model.add(Bidirectional(
                LSTM(lstm_nodes, activation=activation_var,
                     # kernel_regularizer=tensorflow.keras.regularizers.l1(0.01),
                     return_sequences=True),
                input_shape=(train_X.shape[1], train_X.shape[2])))
            model.add(Dropout(0.1))
            model.add(Bidirectional(LSTM(int(lstm_nodes), return_sequences=True, activation=activation_var)))
            model.add(Dropout(0.1))
            model.add(Bidirectional(LSTM(int(lstm_nodes), activation=activation_var)))
            model.add(Dropout(0.1))
            # model.add(layers.Activation(activation_var))
            model.add(Dense(1))
            model.compile(loss=var_loss_eval,
                          optimizer=var_optimizer
                          # ,
                          # metrics=[soft_acc]
                          )
        # fit network
        model.summary()
        history = model.fit(train_X, train_y, epochs=epoch_var, batch_size=batch, validation_data=(test_X, test_y),
                            verbose=0,
                            # shuffle=True,
                            use_multiprocessing=True,
                            callbacks=my_callbacks)
        model.save(Constant.MODLE_BASE_PATH.format(epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval,
                                                   activation_var.__name__ if activation_var else None))
        # plot history
        my_dpi = 96
        fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(1920 / my_dpi, 1080 / my_dpi), sharex=True, sharey=True)
        plt.subplots_adjust(wspace=0.2, hspace=0.5)
        plt.setp(plt.gcf().get_axes(), xticks=[], yticks=[])
        gs = fig.add_gridspec(1, 1)
        ax1 = fig.add_subplot(gs[:, :])
        ax1.plot(history.history['loss'], label='train')
        ax1.plot(history.history['val_loss'], label='test')
        ax1.title.set_text('Loss {}'.format(var_loss_eval.upper()))
        ax1.legend()
        plt.savefig(
            Constant.MODLE_BASE_PATH.format(epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval,
                                            activation_var.__name__ if activation_var else None) + 'plot.png')
        # make a prediction
        yhat = model.predict(test_X)
        test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
        # invert scaling for forecast
        inv_yhat = np.concatenate((yhat, test_X), axis=1)
        inv_yhat = inv_yhat[:, 0]
        # invert scaling for actual
        test_y = test_y.reshape((len(test_y), 1))
        inv_y = np.concatenate((test_y, test_X), axis=1)
        inv_y = inv_y[:, 0]
        # calculate RMSE
        rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
        # mape = self.mean_absolute_percentage_error(inv_y, inv_yhat)
        # mae = mean_absolute_error(inv_y, inv_yhat)  # * 100
        print('Test RMSE: %.3f' % (rmse))
        self.save_stats(epoch_var, lstm_nodes, batch, var_optimizer, var_loss_eval, rmse)
