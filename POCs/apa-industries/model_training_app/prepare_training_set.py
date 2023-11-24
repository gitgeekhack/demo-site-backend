import pandas as pd
import numpy as np
from tqdm import tqdm
from model_training_app.config import Constant, Config

df = pd.read_csv(Constant.RANGE_PREPROCESSED_WITHOUT_PART_ID_DATA_FILE)

train = []
test = []
validate = []

makes = set(df['make'])
categories = set(df['category'])

for make in tqdm(makes, desc='Generating training data'):
    for category in categories:
        x = df[(df['make'] == make)
               & (df['category'] == category)]

        x_valid, x_test, x_train = np.split(x, [int(Config.VALIDATION_DATA_SPLIT_RATIO * len(x)),
                                                int(Config.TEST_DATA_SPLIT_RATIO * len(x))])

        if not x_valid.empty:
            validate.append(x_valid)

        if not x_test.empty:
            test.append(x_test)

        if not x_train.empty:
            train.append(x_train)

df_train = pd.concat(train)
df_train.to_csv(Constant.TRAINING_DATA_FILE_PATH, index=False)
df_test = pd.concat(test)
df_test.to_csv(Constant.TEST_DATA_FILE_PATH, index=False)
df_valid = pd.concat(validate)
df_valid.to_csv(Constant.VALIDATION_DATA_FILE_PATH, index=False)
print(f'Validation:{len(df_valid)}')
print(f'Test:{len(df_test)}')
print(f'Train:{len(df_train)}')