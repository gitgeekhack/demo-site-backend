import pandas


def compare(predicted):
    # predicted = pandas.read_csv('output.csv', converters={i: str for i in range(100)})
    expected = pandas.read_csv('56 DOCS UPDATED.csv', converters={i: str for i in range(100)})
    predicted = predicted.groupby(by=['request_id']).agg('\n'.join)
    for i, row in predicted.iterrows():
        if '\n' in row['document_name']:
            predicted.at[i, 'document_name'] = row['document_name'].split('\n')[0]
    doc_list = predicted['document_name'].to_list()
    # predicted.to_csv("grouped output.csv")

    with open("compare.csv", "w") as f:
        f.write(",".join(expected.keys()) + '\n')

    for i in range(len(expected)):
        expected.loc[[i]].to_csv("compare.csv",
                                 index=False,
                                 header=False,
                                 mode='a')
        if expected.iloc[i]['document_name'] in doc_list:
            doc_index = doc_list.index(expected.iloc[i]['document_name'])
            predicted.iloc[[doc_index]].to_csv("compare.csv",
                                               index=False,
                                               header=False,
                                               mode='a')

        if 'PRE - GPT ' + expected.iloc[i]['document_name'] in doc_list:
            doc_index = doc_list.index('PRE - GPT ' + expected.iloc[i]['document_name'])
            predicted.iloc[[doc_index]].to_csv("compare.csv",
                                               index=False,
                                               header=False,
                                               mode='a')

        else:
            with open("compare.csv", "a") as f:
                f.write("\n")
                f.write("\n")
