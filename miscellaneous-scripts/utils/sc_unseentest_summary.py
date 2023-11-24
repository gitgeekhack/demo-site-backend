import numpy as np
import pandas as pd

category = ["Impression", "SEC_CARE_PLAN", "SEC_DIAGNOSIS", "SEC_GEN_INFO", "SEC_OBJECTIVE", "SEC_PMH_BAD", "SEC_PMH_GOOD", "SEC_REVIEW", "SEC_SUBJECTIVE"]
for i in range(0,5):
    print(f'-------------------------Model_{i} results: ')
    path = f'/home/heli/Documents/result_{i}.csv'
    df = pd.read_csv(path)
    x = 0
    y = 0
    for cat in category:
        x = np.where(df['prediction'].eq(cat))
        y = np.where(df['category'].eq(cat))
        z = len(list(set(x[0]) & set(y[0])))/len(y[0])*100
        print(f'{cat}: '+'{:.2f}%'.format(z))
        x = 0
        y = 0
