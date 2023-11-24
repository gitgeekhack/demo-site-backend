import os
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow

from model_training_app.train_value import TrainModelWithValue
import itertools

epochs = [1000]
lstms = [256]
batch = [1024]
# optimizers = ['adadelta', 'adagrad', 'adam', 'adamax', 'ftrl', 'nadam', 'rmsprop']
optimizers = ['adam']
loss = ['mae']
activation = tensorflow.keras.activations.relu
models = list(itertools.product(epochs, lstms, batch, optimizers, loss))
print("Model combinations needs to be tried", len(models))


def run_models(models):
    o = TrainModelWithValue()
    for model in models:
        print(
            f'<{datetime.now().isoformat()}> = > Epoch: {model[0]}\tLSTM Nodes: {model[1]}\tBatch: {model[2]}\tOptimizer: {model[3]}\tLoss: {model[4]}\t Activation: {activation.__name__ if activation else None}')
        print('=' * 100)
        # try:
        o.run(epoch_var=model[0], lstm_nodes=model[1], batch=model[2], var_optimizer=model[3],
              var_loss_eval=model[4], activation_var=activation)
        # except Exception as e:
        #     print(e)


run_models(models)
print("Process Completed successfully")
