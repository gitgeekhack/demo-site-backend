import os
import pytz
import boto3
import zipfile
import asyncio
import aiofiles
import traceback
import dateparser
from tqdm import tqdm
from queue import Queue
from datetime import datetime
from concurrent import futures
from logging_helper import logger

from dotenv import load_dotenv
load_dotenv()

# Environment Variables
AWS_PROFILE = os.getenv('AWS_PROFILE')
BUCKET_NAME = os.getenv('BUCKET_NAME')
SSE_KEY_PATH = os.getenv('SSE_KEY_PATH')
FRESH_START = os.getenv('FRESH_START')
REFRESH_PROJECTS = eval(os.getenv('REFRESH_PROJECTS'))
DOWNLOAD_FROM_DATE = os.getenv('DOWNLOAD_FROM_DATE')
SAVE_DATASET_PATH = os.getenv('SAVE_DATASET_PATH')
SUCCESSFUL_FILE_PATH = os.getenv('SUCCESSFUL_FILE_PATH')
UNSUCCESSFUL_FILE_PATH = os.getenv('UNSUCCESSFUL_FILE_PATH')

if not AWS_PROFILE:
    logger.error("Configuration incomplete. Please configure AWS_PROFILE environment variable.")
    exit(1)
if not BUCKET_NAME:
    logger.error("Configuration incomplete. Please configure BUCKET_NAME environment variable.")
    exit(1)
if not SSE_KEY_PATH:
    logger.error("Configuration incomplete. Please configure SSE_KEY_PATH environment variable.")
    exit(1)
if not SAVE_DATASET_PATH:
    logger.error("Configuration incomplete. Please configure SAVE_DATASET_PATH environment variable.")
    exit(1)
if not SUCCESSFUL_FILE_PATH:
    logger.error("Configuration incomplete. Please configure SUCCESSFUL_FILE_PATH environment variable.")
    exit(1)
if not UNSUCCESSFUL_FILE_PATH:
    logger.error("Configuration incomplete. Please configure UNSUCCESSFUL_FILE_PATH environment variable.")
    exit(1)

# S3 Constants & SSE KEY
session = boto3.Session()
s3_client = boto3.client('s3')
s3_resource = session.resource('s3')
sse_key = open(SSE_KEY_PATH, "rb")
key = sse_key.read()
bucket = s3_resource.Bucket(BUCKET_NAME)

# Queues for managing file objects
s3_objects_files = Queue()
successful_files = Queue()
unsuccessful_files = Queue()

EXTENSION_TO_UNZIP = ['.gz', '.zip', '.recreated']


async def make_dir(dir_path):
    """ This method is used to make a directory to store annotations """

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


async def unzip(filename):
    """ This method is used to unzip the annotations and images"""

    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(os.path.splitext(filename)[0])


async def parse_date(date):
    """ This method is used to parse the date in the datetime format """

    date = dateparser.parse(date, settings={'RELATIVE_BASE': datetime(1800, 1, 1)})
    if date:
        date = date.replace(tzinfo=pytz.UTC)
        return date
    return None


async def push_files_in_queues(file_path, queue):
    """ This method is used to fill the queue using file objects """

    if os.path.isfile(file_path):
        files = open(file_path, "r")
        for file in files:
            if file != '':
                queue.put(file)


async def get_s3_objects(queue, download_from_dates=None):
    """ This method is used to get the file objects from S3 and push them into queue """

    s3_objects_from_bucket = bucket.objects.all()

    if download_from_dates:
        parsed_download_from_date = await parse_date(DOWNLOAD_FROM_DATE)

        for i, obj in enumerate(s3_objects_from_bucket):
            if obj.last_modified >= parsed_download_from_date:
                queue.put(obj.key)

    else:
        for i, obj in enumerate(s3_objects_from_bucket):
            queue.put(obj.key)


async def load_queues():
    """ This method is used to load all the queues asynchronously """

    logger.info("Loading Objects into Queues...")
    start_time = datetime.utcnow()

    if FRESH_START.lower() == "true":
        loader_coroutines = [get_s3_objects(queue=s3_objects_files, download_from_dates=None)]

    elif FRESH_START.lower() == "false" and DOWNLOAD_FROM_DATE.lower() != 'none':
        loader_coroutines = [get_s3_objects(queue=s3_objects_files, download_from_dates=DOWNLOAD_FROM_DATE)]

    else:
        loader_coroutines = [get_s3_objects(queue=s3_objects_files, download_from_dates=None),
                             push_files_in_queues(file_path=SUCCESSFUL_FILE_PATH, queue=successful_files),
                             push_files_in_queues(file_path=UNSUCCESSFUL_FILE_PATH, queue=unsuccessful_files)]

    await asyncio.gather(*loader_coroutines)

    execution_time = datetime.utcnow() - start_time
    logger.info(f"Successfully loaded objects into Queues in [{execution_time.total_seconds()} seconds]")


async def download_project_annotations(filename, object_name):
    """ This method is used to download the project wise annotations after validating it """

    response = None

    if any(filename.endswith(ext) for ext in EXTENSION_TO_UNZIP):
        if (len(REFRESH_PROJECTS)) == 0 or ('images' in filename) or (
                REFRESH_PROJECTS is not None and any(name in filename for name in REFRESH_PROJECTS)):

            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name.strip(),
                                            SSECustomerKey=key, SSECustomerAlgorithm='AES256')
    else:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name.strip(),
                                        SSECustomerKey=key, SSECustomerAlgorithm='AES256')

    return response


async def download_objects(object_path):
    """ This method is used to download the objects from S3 path and Unzip the annotations and Images"""

    try:
        if object_path not in successful_files.queue:
            object_name = object_path.strip()
            filename = os.path.join(os.getcwd(), SAVE_DATASET_PATH, object_name)

            if filename.endswith('json'):
                return

            response = await download_project_annotations(filename, object_name)
            if response:
                await make_dir(os.path.dirname(filename))

                async with aiofiles.open(filename, "wb") as binary_file:
                    await binary_file.write(response['Body'].read())

                if any(filename.endswith(ext) for ext in EXTENSION_TO_UNZIP):
                    await unzip(filename)

                async with aiofiles.open(SUCCESSFUL_FILE_PATH, "a+") as successful_file:
                    await successful_file.writelines(f'{object_path}\n')

    except (KeyboardInterrupt, Exception) as e:
        async with aiofiles.open(UNSUCCESSFUL_FILE_PATH, "a+") as unsuccessful_file:
            await unsuccessful_file.writelines(f'{object_path}\n')
        logger.error('%s -> %s' % (e, traceback.format_exc()))


def download_handler(object_path):
    """ This method handles the async requests in thread """

    _loop = asyncio.new_event_loop()
    _loop.run_until_complete(download_objects(object_path))


async def main():
    task = []

    try:
        await load_queues()
        with tqdm(total=s3_objects_files.qsize()) as pbar:
            with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
                for _ in range(s3_objects_files.qsize()):
                    object_path = s3_objects_files.get()
                    new_future = executor.submit(download_handler, object_path=object_path)
                    new_future.add_done_callback(lambda x: pbar.update())
                    task.append(new_future)

        futures.wait(task)

    except (KeyboardInterrupt, Exception) as e:
        logger.error('%s -> %s' % (e, traceback.format_exc()))


loop = asyncio.new_event_loop()
loop.run_until_complete(main())