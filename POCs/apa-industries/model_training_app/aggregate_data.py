import pandas as pd
import time

from model_training_app.config import Constant

df = pd.read_csv(Constant.OUTLIER_FILTERED_DATA_FILE_PATH)
cols = ["firstSold", "vehicleMaxQty", "isDevelopment",
        "make", "category", "year", "TotalVIO",
        "SaleYearRank", "HasPartsAuthorityPurchased",
        "HasWorldPacPurchased",
        "HasSSFPurchased"]
df['firstSold'] = pd.to_datetime(df['firstSold'])

# df['firstSold'] = df['firstSold'].apply(lambda x: time.mktime(x.date().timetuple()))
df['firstSold'] = df['firstSold'].apply(lambda x: x.strftime('%Y-%m-%d'))
df = df.groupby(cols).agg('mean').reset_index()
df = df[Constant.PREPROCESSED_WITHOUT_PART_ID_COLUMN_LIST]
df.to_csv(Constant.AGGREGATE_DATA_FILE_PATH, index=False)
