import json
import asyncio
from tqdm import tqdm
file = open("/mnt/dataset_volume/publaynet_fulldataset/publaynet/files/train_formatted_data.json")

data = json.load(file)

check_set = []
target_dir = "/mnt/dataset_volume/publaynet_fulldataset/train/labels/"


async def convert_labels(size, bbox):
    def sorting(l1, l2):
        if l1 > l2:
            lmax, lmin = l1, l2
            return lmax, lmin
        else:
            lmax, lmin = l2, l1
            return lmax, lmin
    xmax, xmin = sorting(bbox[0], bbox[2])
    ymax, ymin = sorting(bbox[1], bbox[3])
    dw = 1./size[1]
    dh = 1./size[0]
    x = (xmin + xmax)/2.0
    y = (ymin + ymax)/2.0
    w = xmax - xmin
    h = ymax - ymin
    x = round(x*dw,6)
    w = round(w*dw,6)
    y = round(y*dh,6)
    h = round(h*dh,6)
    return (x,y,w,h)


async def temp():
    for i in tqdm(data["data"]):
        filename = i["file_name"].rsplit(".")[0]
        filepath = target_dir + filename + ".txt"
        if len(i["annotations"]) != 0:
            for x in range(len(i["annotations"])):
                for y in range(len(i["annotations"][x])):
                    category_id = i["annotations"][x][y]["category_id"] - 1
                    bbox = i["annotations"][x][y]["bbox"]
                    kitti_bbox = [bbox[0], bbox[1], bbox[2] + bbox[0], bbox[3] + bbox[1]]
                    yolo_bbox = await convert_labels((i["height"], i["width"]),
                                                     (kitti_bbox[0], kitti_bbox[1], kitti_bbox[2], kitti_bbox[3]))
                    content = str(category_id) + " " + str(yolo_bbox[0]) + " " + str(yolo_bbox[1]) + " " + str(
                        yolo_bbox[2]) + " " + str(yolo_bbox[3])
                    # Append to file files
                    file = open(filepath, "a+")
                    file.write(content)
                    file.write("\n")
                    file.close()
        else:
            check_set.append(filename)
            # Write files
            with open(filepath, "w") as write_file:
                pass


async def main():
    await temp()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


