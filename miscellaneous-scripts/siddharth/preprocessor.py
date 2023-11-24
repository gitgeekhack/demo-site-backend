import pandas as pd

df = pd.read_csv("more_samples.csv")


df['FilePath'] = df['DocumentS3URL'].apply(lambda x: x.replace('https://pareit-dev-datalabeling-anno.s3.us-east-2.amazonaws.com/', ''))
df['FilePath'] = df['FilePath'].apply(lambda x: x.replace('https://pareit-dev-datalabeling-anno-hash.s3.us-east-2.amazonaws.com/', ''))
df['FilePath'] = df['FilePath'].apply(lambda x: x.replace('+', ' '))
df['FilePath'] = "./more_samlpes/"+ df['FilePath']
df.to_csv('more_samlpes_preprocessed.csv', index=False)
