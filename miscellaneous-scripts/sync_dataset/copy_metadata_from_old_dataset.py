import os
import asyncio
import shutil
import traceback
from glob import glob
from tqdm import tqdm
from queue import Queue
from datetime import datetime
from concurrent import futures
from logging_helper import logger

from dotenv import load_dotenv
load_dotenv()

# Environment Variables
SOURCE_FOLDER_PATH = os.getenv('SOURCE_FOLDER_PATH')
DESTINATION_FOLDER_PATH = os.getenv('DESTINATION_FOLDER_PATH')

if not SOURCE_FOLDER_PATH:
    logger.error("Configuration incomplete. Please configure SOURCE_FOLDER_PATH environment variable.")
    exit(1)
if not DESTINATION_FOLDER_PATH:
    logger.error("Configuration incomplete. Please configure DESTINATION_FOLDER_PATH environment variable.")
    exit(1)

# Queues for managing file objects
source_queue = Queue()
destination_queue = Queue()


async def push_files_in_queues(directory_path, queue):
    """ This method is used to fill the queue using file objects """

    paths = glob(f"{directory_path}/*/**", recursive=True)
    if paths:
        for path in paths:
            path = path.replace(f'{directory_path}/', '')
            queue.put(path)


async def load_queues():
    """ This method is used to load all the queues asynchronously """

    logger.info("Loading Objects into Queues...")
    start_time = datetime.utcnow()

    loader_coroutines = [push_files_in_queues(directory_path=SOURCE_FOLDER_PATH, queue=source_queue),
                         push_files_in_queues(directory_path=DESTINATION_FOLDER_PATH, queue=destination_queue)]

    await asyncio.gather(*loader_coroutines)

    execution_time = datetime.utcnow() - start_time
    logger.info(f"Successfully loaded objects into Queues in [{execution_time.total_seconds()} seconds]")


async def copy_objects(object_path):
    """ This method is used to download the objects from S3 path and Unzip the annotations and Images"""

    try:
        if object_path not in destination_queue.queue:
            object_name = object_path.strip()
            source_path = os.path.join(SOURCE_FOLDER_PATH, object_name)
            destination_path = os.path.join(DESTINATION_FOLDER_PATH, object_name)

            if os.path.isdir(source_path):
                os.makedirs(destination_path, exist_ok=True)
            else:
                dir_path = os.path.dirname(destination_path)
                os.makedirs(dir_path, exist_ok=True)
                shutil.copy(source_path, destination_path)

    except (KeyboardInterrupt, Exception) as e:
        logger.error('%s -> %s' % (e, traceback.format_exc()))


def copy_handler(object_path):
    """ This method handles the async requests in thread """

    _loop = asyncio.new_event_loop()
    _loop.run_until_complete(copy_objects(object_path))


async def main():
    task = []

    try:
        await load_queues()
        with tqdm(total=source_queue.qsize()) as pbar:
            with futures.ProcessPoolExecutor(os.cpu_count() - 1) as executor:
                for idx in range(source_queue.qsize()):
                    object_path = source_queue.get()
                    new_future = executor.submit(copy_handler, object_path=object_path)
                    new_future.add_done_callback(lambda x: pbar.update())
                    task.append(new_future)

        futures.wait(task)

    except (KeyboardInterrupt, Exception) as e:
        logger.error('%s -> %s' % (e, traceback.format_exc()))


loop = asyncio.new_event_loop()
loop.run_until_complete(main())
