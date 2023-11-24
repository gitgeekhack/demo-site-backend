import asyncio
import os
from queue import Queue

import aiofiles as aiofiles
import boto3
from tqdm import tqdm

os.environ['AWS_PROFILE'] = "pareit-dev"
os.environ['AWS_DEFAULT_REGION'] = "us-east-2"

FILE_LIST_PATH = "more_samples_all_files.txt"  # file contains list of filenames to be downloaded from s3
SUCCESSFULLY_DOWNLOADED_LIST_PATH = "./successfully_downloaded.txt"  # file contains list of filenames that are successfully downloaded
UNSUCCESSFULLY_DOWNLOADED_LIST_PATH = "./unsuccessfulfiles.txt"  # file contains list of filenames that couldn't complete the download process
SSE_KEY_PATH = "s3_sse_key.bin"  # file contains SSE C Decryption key
SAVE_FOLDER_NAME = 'more_samlpes'

BUCKET = 'pareit-dev-datalabeling-anno-hash'

SSE_KEY = open(SSE_KEY_PATH, "rb")
KEY = SSE_KEY.read()
s3 = boto3.client('s3')

files_q = Queue()
successful_q = Queue()
unsuccessful = Queue()
pbar = tqdm(total=471)


async def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


async def push_in_queues_from_file(file_path, queue):
    if os.path.isfile(file_path):
        f = open(file_path, "r")
        for x in f:
            if x != '':
                queue.put(x.replace('\n', ''))


async def load_queues():
    loader_coroutines = [push_in_queues_from_file(file_path=FILE_LIST_PATH, queue=files_q),
                         push_in_queues_from_file(file_path=SUCCESSFULLY_DOWNLOADED_LIST_PATH, queue=successful_q),
                         push_in_queues_from_file(file_path=UNSUCCESSFULLY_DOWNLOADED_LIST_PATH, queue=unsuccessful)]
    await asyncio.gather(*loader_coroutines)


async def download_from_s3():
    while not files_q.empty():
        object_name = await get_object_from_queue_async()
        try:
            file_path = SAVE_FOLDER_NAME + object_name
            if not (object_name in successful_q.queue):
                object_name = object_name.strip()
                filename = os.path.join(os.getcwd(), SAVE_FOLDER_NAME, object_name)
                response = await s3_download_async(object_name)
                await make_dir(os.path.dirname(filename))
                async with aiofiles.open(filename, "wb") as binary_file:
                    await binary_file.write(response['Body'].read())
                await update_success_queue(object_name)
        except (KeyboardInterrupt, Exception) as e:
            print(e)
            print(object_name)
            print("-" * 300)
            await update_unsuccessful_queue(object_name)
        finally:
            pbar.update()


async def update_unsuccessful_queue(object_name):
    unsuccessful.put(object_name)
    async with aiofiles.open(UNSUCCESSFULLY_DOWNLOADED_LIST_PATH, "a") as unsuccessful_obj:
        await unsuccessful_obj.write(object_name + "\n")


async def update_success_queue(object_name):
    successful_q.put(object_name)
    async with aiofiles.open(SUCCESSFULLY_DOWNLOADED_LIST_PATH, "a") as successful_obj:
        await successful_obj.write(object_name + "\n")


async def get_object_from_queue_async():
    object_name = files_q.get()
    return object_name


async def s3_download_async(object_name):
    r = s3.get_object(Bucket=BUCKET, Key=object_name.strip(), SSECustomerKey=KEY, SSECustomerAlgorithm='AES256')
    return r


async def main():
    await load_queues()
    download_coroutines = [download_from_s3() for _ in range(1)]
    await asyncio.gather(*download_coroutines)


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
