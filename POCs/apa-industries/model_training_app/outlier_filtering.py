import pandas as pd
import numpy as np

from scipy import stats
from model_training_app.config import Config, Constant


df = pd.read_csv(Constant.PREPROCESSED_WITHOUT_PART_ID_DATA_FILE)
# df = pd.read_csv(Constant.FIRST_SALE_YEAR_DATA_FILE_PATH)
print('Actual', len(df))

out = df[np.abs(stats.zscore(df['units_sold'])) > Config.OUTLIER_THRASH]
print('Outliers', len(out))
out.to_csv(Constant.OUTLIER_DATA_FILE_PATH, index=False)
df = df[np.abs(stats.zscore(df['units_sold'])) < Config.OUTLIER_THRASH]
print('New data ', len(df))

df.to_csv(Constant.OUTLIER_FILTERED_DATA_FILE_PATH, index=False)
