import asyncio
import csv
import glob
import os

from dsutils import filter_annotation_path_by_project, get_annotation_full_path
from dsutils.cvat import CVATHelper
from tqdm import tqdm

DATASET_PATH = '/home/heli/Documents/git/PareIT/pareit-miscellaneous-scripts/test/test2'
SUMMARY_CSV_PATH = '/home/heli/Documents/git/PareIT/pareit-miscellaneous-scripts/test/test2/summary.csv'
files = glob.glob(os.path.join(DATASET_PATH, '*'))
projects = ['Filename', 'Split_Turn', 'Named Entities', 'Medical Entities', 'Document Structure',
            'Handwritten_Checkbox',
            'Sections', 'Total']


async def csv_writer(summary):
    with open(SUMMARY_CSV_PATH, 'a+', encoding='UTF-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=projects)
        writer.writeheader()
        writer.writerows(summary)


async def main():
    summary_all = []
    try:
        for path in tqdm(files):
            summary = {'Filename': path.split(DATASET_PATH)[-1]}
            for name in projects:
                annotations = await filter_annotation_path_by_project(name, path)
                if name == 'Split_Turn' and not annotations:
                    annotations = [os.path.dirname(os.path.dirname(file)) for file in
                                   glob.glob(f'{path}/{name}*/annotations.xml')]
                if annotations:
                    paths = [await CVATHelper(xml_path=await get_annotation_full_path(anno_root_folder=i, project=name))
                             for
                             i in annotations] if annotations else None
                    summary[name] = sum([int(path.annotations['annotations']['meta']['task']['size']) for path in
                                         paths]) if paths else None
            summary['Total'] = sum(value for key, value in summary.items() if key != 'Filename')
            summary_all.append(summary)
        print(summary_all)

    except (KeyboardInterrupt, Exception) as e:
        print(e)

    await csv_writer(summary_all)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
