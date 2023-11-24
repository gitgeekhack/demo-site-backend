import json
import pandas as pd
from tqdm import tqdm
from model_training_app.config import Constant

df = pd.read_csv(Constant.PREPROCESSED_WITH_PART_ID_DATA_FILE)

out = []

part_ids = set(df['id'].tolist())

for part_id in tqdm(part_ids, desc="Filter training data by first sales year"):
    x = df[df['id'] == part_id]
    min_year = min(x['year'])
    out.append(x[x['year'] == min_year])

out_df = pd.concat(out)
out_df = out_df[Constant.PREPROCESSED_WITHOUT_PART_ID_COLUMN_LIST]
out_df.to_csv(Constant.FIRST_SALE_YEAR_DATA_FILE_PATH, index=False)
