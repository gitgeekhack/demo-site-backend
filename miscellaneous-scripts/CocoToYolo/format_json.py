import json
import asyncio
from tqdm  import tqdm

annot_file = open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/train.json")
data = json.load(annot_file)
f = open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/files/file_details.txt")
incomplete_annots = json.load(f)
print("data loaded")

pbar = tqdm(total=len(incomplete_annots))

async def main():
    d = {}
    image_annot = {}
    for x in data["annotations"]:
        if x["image_id"] in image_annot.keys():
            image_annot[x["image_id"]].append(x)
        else:
            image_annot[x["image_id"]] = []

    for annot in incomplete_annots:
        annot['annotations'].append(image_annot[annot['id']])
        pbar.update()

    d["data"] = incomplete_annots
    write_data = json.dumps(d)
    with open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/files/train_formatted_data.json", "w") as write_file:
        write_file.write(write_data)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
