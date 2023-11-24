import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.genmod.families.links import probit
from scipy import stats

threshold = 5

df = pd.read_csv('data_without_id.csv')
print('Actual', len(df))

out = df[np.abs(stats.zscore(df['units_sold'])) > threshold]
print('Outliers', len(out))
out.to_csv('outlier_points.csv', index=False)
df = df[np.abs(stats.zscore(df['units_sold'])) < threshold]
print('New data ', len(df))

df.to_csv('outlier_removed.csv', index=False)
#
# sns.boxplot(x=df['units_sold'])
# plt.show()
