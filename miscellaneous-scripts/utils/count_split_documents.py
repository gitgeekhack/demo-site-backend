import os
import re

DIR = "/home/heli/Documents/git/pareIT-internal/download_dataset"
paths = os.listdir(DIR)

sum = 0
for path in paths:
    file_path = os.listdir(DIR + '/' + path)
    files = list(filter(lambda v: re.match('\d{1,2}-{1}\d{1,2}', v), file_path))
    sum = sum + len(files)

print(sum)