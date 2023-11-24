import torch


import cv2
import pytesseract as tess
import pandas as pd
import os
import re

from constants import DL_path
from crop import DetectionHelper



# Model
model = torch.hub.load(DL_path.yolo_path, 'custom', path=DL_path.model_path)
model.conf = 0.5
allowed_classes = ['address', 'date_of_birth', 'exp_date', 'license_number', 'name']

img_path = "D:/Office/veronica/data/Driver_License/test-images/DL-Khushbu-2.jpg"


def get_classes(class_file_name):
    names = {}
    with open(class_file_name, 'r') as data:
        for ID, name in enumerate(data):
            names[ID] = name.strip('\n')
    return names

original_img = cv2.imread(img_path)
results = model(img_path)
results.show()
dl = DetectionHelper()



class_names = get_classes("D:/Office/veronica/model_training_app/driver_license/DL.names")

text_dict = dict(zip(class_names.values(), [None] * len(class_names.values())))
data = pd.DataFrame(results.pred[0]).sort_values(by = 4, ascending = True)
data = data.values.tolist()
for i in range(len(data)):
    box = data[i]
    img = dl.crop_object(original_img,coordinates=box[:4])
    string = dl.gettext(img)
    labels = allowed_classes[int(data[i][5])]
    print(string)
    string = (string.strip())
    string = string.replace("\n", "")
    text_dict[labels]=string
    if labels == "date_of_birth" or labels == "exp_date":
        regex = "^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}$"
        match = re.search(regex, string)
        text = match.group() if match else None

print(text_dict)
