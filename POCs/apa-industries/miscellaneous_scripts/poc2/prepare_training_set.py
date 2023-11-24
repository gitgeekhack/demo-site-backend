import pandas as pd
import numpy as np
from tqdm import tqdm

df = pd.read_csv('outlier_removed.csv')

train = []
test = []
validate = []

makes = set(df['make'])
categories = set(df['category'])

for make in tqdm(makes, desc='Generating training data'):
    for category in categories:
        x = df[(df['make'] == make)
               & (df['category'] == category)]

        x_valid, x_test, x_train = np.split(x, [int(.1 * len(x)), int(.3 * len(x))])

        if not x_valid.empty:
            validate.append(x_valid)

        if not x_test.empty:
            test.append(x_test)

        if not x_train.empty:
            train.append(x_train)

df_train = pd.concat(train)
df_train.to_csv('Training_data.csv', index=False)
df_test = pd.concat(test)
df_test.to_csv('Test_data.csv', index=False)
df_valid = pd.concat(validate)
df_valid.to_csv('Valid_data.csv', index=False)
