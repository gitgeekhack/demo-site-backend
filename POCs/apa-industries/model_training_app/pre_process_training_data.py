import json
from datetime import datetime

import pandas as pd
from tqdm import tqdm
from model_training_app.config import Constant

f = open(Constant.DATA_FILE_PATH, 'r')

data = json.load(f)

rows = []
failed = []
for i in tqdm(range(len(data)), desc="Pre-Processing Records"):
    try:
        id = data[i]['id']
        firstSold = data[i]['firstSold']
        vehicleMaxQty = data[i]['vehicleMaxQty']
        isDevelopment = data[i]['isDevelopment']
        makes = data[i]['makes']
        category = data[i]['category']
        vio_us = data[i]['vio_us']
        vio_ca = data[i]['vio_ca']
        sales = data[i]['units']['totals']
        partType = data[i]['partType']
        subCat = data[i]['subCat']
        units_sold_360 = sales['TotalUnits']['360']
        for make in makes:
            for year, units_sold in sales['TotalUnits'].items():
                try:
                    t = sales["WP"]
                    wp = True
                except Exception as e:
                    wp = False
                try:
                    t = sales["PA"]
                    pa = True
                except Exception as e:
                    pa = False
                try:
                    t = sales["SSF"]
                    ssf = True
                except Exception as e:
                    ssf = False
                rows.append([units_sold_360,
                             units_sold, id, partType,
                             firstSold,
                             vehicleMaxQty,
                             isDevelopment,
                             make,
                             category, subCat,
                             vio_us,
                             vio_ca,
                             year,
                             wp,
                             pa,
                             ssf])
    except Exception as e:
        print(e)
        print(data[i])
        failed.append(data[i])

    # break
df = pd.DataFrame(columns=["units_sold_360", "units_sold", "id", "partType",
                           "firstSold",
                           "vehicleMaxQty",
                           "isDevelopment",
                           "make",
                           "category", "subCat",
                           "vio_us",
                           "vio_ca",
                           "year",
                           "HasWorldPacPurchased",
                           "HasPartsAuthorityPurchased",
                           "HasSSFPurchased"
                           ], data=rows)
df['firstSold'] = pd.to_datetime(df['firstSold'], unit='ms')
df['year'] = df['year'].apply(lambda x: int(x))
df = df[df['year'] != 360]
# df = df[df['year'] != 2021]
df['TotalVIO'] = df['vio_us'] + df['vio_ca']


def find_range(x):
    if x >= 1 and x <= 25:
        return "[1 - 25]"
    elif x >= 26 and x <= 50:
        return "[26 - 50]"
    elif x >= 26 and x <= 50:
        return "[26 - 50]"
    elif x >= 51 and x <= 150:
        return "[51 - 150]"
    elif x >= 151 and x <= 300:
        return "[151 - 300]"
    elif x >= 301 and x <= 500:
        return "[301 - 500]"
    elif x >= 501 and x <= 1000:
        return "[501 - 1000]"
    elif x >= 1001 and x <= 2500:
        return "[1001 - 2500]"
    elif x >= 2501 and x <= 5000:
        return "[2501 - 5000]"
    else:
        return "[ > 5000]"


def find_range_int(x):
    if x >= 1 and x <= 25:
        return 1

    elif x >= 26 and x <= 50:
        return 2
    elif x >= 26 and x <= 50:
        return 3
    elif x >= 51 and x <= 150:
        return 4
    elif x >= 151 and x <= 300:
        return 5
    elif x >= 301 and x <= 500:
        return 6
    elif x >= 501 and x <= 1000:
        return 7
    elif x >= 1001 and x <= 2500:
        return 8
    else:
        return 9


def find_year_rank(x):
    v = int(x['year']) - x['firstSold'].year
    return v  # + 1


def find_no_days(x):
    if x['year'] == datetime.now().year and x['firstSold'].year == datetime.now().year:
        d1 = datetime.now()
        delta = d1 - x['firstSold']
        return 1 if delta.days <= 0 else delta.days
    elif x['year'] == datetime.now().year and x['firstSold'].year != datetime.now().year:
        d1 = datetime.now()
        d0 = datetime.strptime('{}-01-01'.format(x['year']), "%Y-%m-%d")
        delta = d1 - d0
        return 1 if delta.days <= 0 else delta.days
    elif x['year'] == x['firstSold'].year:
        d1 = datetime.strptime('{}-12-31'.format(x['year']), "%Y-%m-%d")
        delta = d1 - x['firstSold']
        return 1 if delta.days <= 0 else delta.days
    # elif x['year'] = x['firstSold'].year:
    #     d1 = datetime.strptime('{}-12-31'.format(x['year']), "%Y-%m-%d")
    #     delta = d1 - x['firstSold']
    #     return delta.days
    else:
        return 365

def extrapolate(x):
    days = x['no_of_days']
    sales = x['units_sold']
    new_sales = (365 * sales) / days
    return int(new_sales)

df['no_of_days'] = df.apply(lambda x: find_no_days(x), axis=1)
df['units_sold'] = df.apply(lambda x: extrapolate(x), axis=1)
df['firstSold'] = pd.to_datetime(df['firstSold'])

df['sale_year_rank'] = df.apply(lambda x: find_year_rank(x), axis=1)
df['firstSold'] = df['firstSold'].apply(lambda x: x.strftime('%Y-%m-%d'))
df['vehicleMaxQty'] = df['vehicleMaxQty'].apply(lambda x: 1 if x == 0 else x)
df = df[df['TotalVIO'] != 0]
# df['sales_range'] = df['units_sold'].apply(lambda x: find_range(x))
df = df.sample(frac=1).reset_index(drop=True)
df = df[Constant.PREPROCESSED_WITHOUT_PART_ID_COLUMN_LIST]
df.to_csv(Constant.PREPROCESSED_WITHOUT_PART_ID_DATA_FILE, index=False)
# df = df[Constant.PREPROCESSED_WITHOUT_PART_ID_COLUMN_LIST]
# df.to_csv(Constant.PREPROCESSED_WITHOUT_PART_ID_DATA_FILE, index=False)
print('Pre-Processing completed successfully')
print('Failed to Process records:', len(failed))
