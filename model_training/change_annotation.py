import os
import pandas as pd
import numpy as np
from tqdm import tqdm
directory = '/home/heli/Desktop/git/demo-site-backend/data/driving_license/labels'

for filename in tqdm(os.listdir(directory)):
    print(filename)
    f = os.path.join(directory, filename)
    df = pd.read_csv(f, sep=" ", header=None)
    df = df.dropna(axis=1)
    df.columns = ['label', 'x0', 'y0', 'x1', 'y1']

    # print(df['label'])
    df['label'] = np.where(df['label'] ==4, 3, df['label'])
    df['label'] = np.where(df['label'] == 5, 3, df['label'])
    df['label'] = np.where(df['label'] >= 6, df['label']-2, df['label'])
    # print(df['label'])
    # print(df)
    with open(f'/home/heli/Desktop/git/demo-site-backend/data/driving_license/new_labels/{filename}', 'a') as f:
        dfAsString = df.to_string(header=False, index=False)
        f.write(dfAsString)
