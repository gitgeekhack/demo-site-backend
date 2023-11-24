import os
from tqdm import tqdm
import asyncio

ALL_ANNOTATED_LABELS_PATH = os.getenv('ALL_ANNOTATED_LABELS_PATH')
TARGET_DIR = os.getenv('TARGET_DIR')

async def modify_annots(all_annots_data):
    new_data = []
    for a_data in all_annots_data:
        annot_list = a_data.rsplit(" ")
        if int(annot_list[0]) == 0:
            new_data.append(a_data)
        elif int(annot_list[0]) in [2,4, 8]:
            new_data.append(" ".join([str(1), *annot_list[1:]]))
        elif int(annot_list[0]) ==3:
            new_data.append(" ".join([str(2), *annot_list[1:]]))
        elif int(annot_list[0]) == 5:
            new_data.append(" ".join([str(4), *annot_list[1:]]))
        elif int(annot_list[0]) == 6:
            new_data.append(" ".join([str(3), *annot_list[1:]]))
        elif int(annot_list[0]) == 7:
            new_data.append(" ".join([str(5), *annot_list[1:]]))
        else:
            new_data.append(" ".join([str(0), *annot_list[1:]]))
    return new_data

async def main():
    for annot_file in tqdm(annot_files):
        all_annots_file_path = os.path.join(ALL_ANNOTATED_LABELS_PATH, annot_file)
        with open(all_annots_file_path, "r") as read_file:
            all_annots_data = read_file.readlines()

        merged_annots = await modify_annots(all_annots_data)
        with open(os.path.join(TARGET_DIR, annot_file), "w") as write_file:
            write_file.writelines(merged_annots)


if __name__=="__main__":
    os.makedirs(TARGET_DIR, exist_ok=True)

    annot_files = os.listdir(ALL_ANNOTATED_LABELS_PATH)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())