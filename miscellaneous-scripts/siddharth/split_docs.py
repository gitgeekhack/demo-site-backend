import pandas as pd

df = pd.read_csv("more_samples.csv")

import fitz


def split_files(x):
    file_path = x['FilePath']
    start = x['ParentStartPage'] - 1
    end = x['ParentEndPage'] - 2
    try:
        doc = fitz.open(file_path)
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, start, end)
        new_doc.save(file_path.replace('more_samlpes', 'more_splitted_test'))
    except Exception as e:
        print(file_path, e)
    return file_path.replace('more_samlpes', 'more_splitted_test')


df['FilePath'] = df.apply(lambda x: split_files(x), axis=1)
df.to_csv('more_samples_split.csv', index=False)
