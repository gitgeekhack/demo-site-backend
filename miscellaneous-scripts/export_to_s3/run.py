import asyncio
from app.export_task import ExportTasks
from concurrent import futures
from tqdm import tqdm
import os


export_task_obj = ExportTasks()


def export_task_process_handler(task):
    _loop = asyncio.new_event_loop()
    x = _loop.run_until_complete(export_task_obj.export_task_long_process(task))
    return x


async def main():
    tasks = await export_task_obj.get_tasks_by_status_and_project(statuses=["completed", "validation"],
                                                                  projects=["Named Entities"],
                                                                  reviewers=['user'])
    print("No of Tasks to export:", len(tasks))

    task_pool = []

    with tqdm(total=len(tasks)) as pbar:
        with futures.ProcessPoolExecutor(os.cpu_count()-1) as executor:
            for task in tasks:
                new_future = executor.submit(export_task_process_handler, task=task)
                new_future.add_done_callback(lambda x: pbar.update())
                task_pool.append(new_future)
    result = futures.wait(task_pool)

if __name__ == '__main__':
    l = asyncio.get_event_loop()
    l.run_until_complete(main())
