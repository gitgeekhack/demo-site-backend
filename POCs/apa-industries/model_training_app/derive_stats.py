import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
df = pd.read_csv('Validation_test_results1.csv')


def get_sale_range(x):
    if x > 0 and x <= 500:
        return '1 to 500'
    elif x > 500 and x <= 1500:
        return '500 to 1500'
    elif x > 1500 and x <= 3000:
        return '1500 to 3000'
    elif x > 3000 and x <= 5000:
        return '3000 to 5000'
    else:
        return '> 5000'


def get_diff_range(x):
    if -50 <= x <= 50:
        return '-50 to 50'
    elif -100 <= x <= 100:
        return '-100 to 100'
    elif -250 <= x <= 250:
        return '-250 to 250'
    else:
        return '< -250 & > 250'


df['SalesRange'] = df['Actual'].apply(lambda x: get_sale_range(x))
df['DiffRange'] = df['Diff'].apply(lambda x: get_diff_range(x))
sale_range = set(df['SalesRange'].tolist())
diff_range = set(df['DiffRange'].tolist())
l = len(df)
print(df.head())
stats = []
for diff in diff_range:
    for sale in sale_range:
        l = len(df[(df['SalesRange'] == sale)])
        x = len(df[(df['SalesRange'] == sale)
                   & (df['DiffRange'] == diff)])
        if x > 0:
            v = (x / l) * 100
            stats.append([sale, diff, l, x, round(v, 2)])
print()
stats_df = pd.DataFrame(
    columns=['ActualSales', 'ForecastDiff', "TotalParts", "NoOfPartsWithDiffs", 'Volume Coverage %'], data=stats)
print(stats_df)
stats_df.sort_values(['ActualSales', 'ForecastDiff'], inplace=True)
stats_df.to_csv('Volume_stats_new_best.csv', index=False)
