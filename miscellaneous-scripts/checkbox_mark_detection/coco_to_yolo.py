import json

file = open("./train_checkbox_mark_dataset.json")
data = json.load(file)

check_set = []
target_dir = "./yolo_labels/"


# convert bounding box and labels
def convert_labels(size, bbox):
    def sorting(l1, l2):
        if l1 > l2:
            lmax, lmin = l1, l2
            return lmax, lmin
        else:
            lmax, lmin = l2, l1
            return lmax, lmin

    xmax, xmin = sorting(bbox[0], bbox[2])
    ymax, ymin = sorting(bbox[1], bbox[3])
    dw = 1. / size[1]
    dh = 1. / size[0]
    x = (xmin + xmax) / 2.0
    y = (ymin + ymax) / 2.0
    w = xmax - xmin
    h = ymax - ymin
    x = round(x * dw, 6)
    w = round(w * dw, 6)
    y = round(y * dh, 6)
    h = round(h * dh, 6)
    return [x, y, w, h]


# check that YOLO bounding box is valid or not
def check_valid(bbox_list):
    bbox = []
    for x in range(0, 4):
        if float(bbox_list[x]) > 1.0:
            bbox_list[x] = 1.0
        bbox.append(abs(bbox_list[x]))
    return bbox


# iterate through the annotation values
for i in data["annotations"]:
    filename = i['image_name'].rsplit("/")[-1].rsplit(".")[0]
    filepath = target_dir + filename + ".txt"
    height = width = 0
    if len(i) != 0:
        for x in range(0, len(data['images'])):
            if data['images'][x]['file_name'] == i['image_name']:
                height = data['images'][x]['height']
                width = data['images'][x]['width']
                break
        category_id = str(i['category_id'])
        bbox = i['bbox']
        kitti_bbox = [bbox[0], bbox[1], bbox[2] + bbox[0], bbox[3] + bbox[1]]
        yolo_bbox = convert_labels((height, width), (kitti_bbox[0], kitti_bbox[1], kitti_bbox[2], kitti_bbox[3]))
        yolo_bbox = check_valid(yolo_bbox)
        content = category_id + " " + str(yolo_bbox[0]) + " " + str(yolo_bbox[1]) + " " + str(yolo_bbox[2]) + " " + str(
            yolo_bbox[3])
        file = open(filepath, "a+")
        file.write(content)
        file.write("\n")
        file.close()
    else:
        check_set.append(filename)
        with open(filepath, "w") as write_file:
            pass
