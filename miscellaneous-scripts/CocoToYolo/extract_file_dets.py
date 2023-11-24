import json
import asyncio

annot_file = open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/train.json")
data = json.load(annot_file)

complete_annots = []
incomplete_annots = []


async def check_annot(annot_obj):
    if "corrected" in annot_obj.keys():
        complete_annots.append(annot_obj)
    else:
        annot_obj["annotations"] = []
        incomplete_annots.append(annot_obj)



async def main():
    check_corrected_coros = []
    for x in data["images"]:
        check_corrected_coros.append(check_annot(x))
    await asyncio.gather(*check_corrected_coros)
    file_dets = json.dumps(incomplete_annots)
    with open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/files/file_details.txt", "w") as f:
        f.write(file_dets)

    has_annot = json.dumps(complete_annots)
    with open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/files/has_annotations.txt", "w") as write_file:
        write_file.write(has_annot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

