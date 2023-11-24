import asyncio
import os
import zipfile
from glob import glob

DIR = '/mnt/dataset_volume/hashed_dataset_08122022'

all_files = glob(f"{DIR}/*/**", recursive=True)
EXTENSION = ['.gz', '.zip']


async def unzip(filename):
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(os.path.splitext(filename)[0])


async def main():
    try:
        for file in all_files:
            if any(file.endswith(ext) for ext in EXTENSION):
                await unzip(file)
    except Exception as e:
        print(e)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
