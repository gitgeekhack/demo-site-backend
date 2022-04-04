import torch
import os

YOLOV5_PATH = 'ultralytics/yolov5:v6.0'
CUSTOM_MODEL_PATH = '/home/heli/Desktop/git/demo-site-backend/model_training/model/driving_license/dl-01042022.pt'

model = torch.hub.load(YOLOV5_PATH, 'custom',path=CUSTOM_MODEL_PATH,force_reload=True)
model.conf = 0.49
directory = '/home/heli/Desktop/git/demo-site-backend/data/driving_license/test-images/indian-dl'

for filename in os.listdir(directory):
    path = os.path.join(directory, filename)
    results = model(path)
    results.save('/home/heli/Desktop/git/demo-site-backend/model_training/temp/')
