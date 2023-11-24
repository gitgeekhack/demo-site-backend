import json
import pandas as pd

f = open('apa_response.json', 'r')

data = json.load(f)

rows = []
failed = []
for i in range(len(data)):
    try:
        id = data[i]['id']
        firstSold = data[i]['firstSold']
        vehicleMaxQty = data[i]['vehicleMaxQty']
        isDevelopment = data[i]['isDevelopment']
        makes = data[i]['makes']
        category = data[i]['category']
        vio_us = data[i]['vio_us']
        vio_ca = data[i]['vio_ca']
        sales = data[i]['units']
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
                rows.append([units_sold, id,
                             firstSold,
                             vehicleMaxQty,
                             isDevelopment,
                             make,
                             category,
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
df = pd.DataFrame(columns=["units_sold", "id",
                           "firstSold",
                           "vehicleMaxQty",
                           "isDevelopment",
                           "make",
                           "category",
                           "vio_us",
                           "vio_ca",
                           "year",
                           "HasPartsAuthorityPurchased",
                           "HasWorldPacPurchased",
                           "HasSSFPurchased"
                           ], data=rows)
df['firstSold'] = pd.to_datetime(df['firstSold'], unit='ms')
df['year'] = df['year'].apply(lambda x: int(x))
df = df[df['year'] != 360]
df['TotalVIO'] = df['vio_us'] + df['vio_ca']


def find_year_rank(x):
    v = int(x['year']) - x['firstSold'].year
    return v + 1


df['SaleYearRank'] = df.apply(lambda x: find_year_rank(x), axis=1)
df = df[["units_sold", "id", "firstSold", "vehicleMaxQty", "isDevelopment", "make", "category", "year", "TotalVIO",
         "SaleYearRank", "HasPartsAuthorityPurchased",
                           "HasWorldPacPurchased",
                           "HasSSFPurchased"]]
print(df)
print('failed:', len(failed))
df.to_csv('data_with_id.csv', index=False)
df = df[["units_sold", "firstSold", "vehicleMaxQty", "isDevelopment", "make", "category", "year", "TotalVIO",
         "SaleYearRank", "HasPartsAuthorityPurchased",
                           "HasWorldPacPurchased",
                           "HasSSFPurchased"]]
print(df)
df.to_csv('data_without_id.csv', index=False)
