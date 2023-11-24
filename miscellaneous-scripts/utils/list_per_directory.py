from glob import glob

DIR = "/home/heli/Documents/git/pareIT-internal/download_dataset"
TEXT_FILE_PATH = r'/home/heli/Documents/git/PareIT/pareit-miscellaneous-scripts/stats/successfully_downloaded.txt'

x = glob(f"{DIR}/*/**", recursive=True)

with open(TEXT_FILE_PATH, 'w+') as fp:
    for item in x:
        fp.write("%s\n" % item)
    print('Done')
