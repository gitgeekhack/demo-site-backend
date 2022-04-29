import torch
import os

YOLOV5_PATH = 'ultralytics/yolov5:v6.0'
CUSTOM_MODEL_PATH = '/home/heli/Desktop/git/demo-site-backend/model_training/model/driving_license/DLObjectDetection.pt'

model = torch.hub.load(YOLOV5_PATH, 'custom',path=CUSTOM_MODEL_PATH,force_reload=True)
model.conf = 0.49
directory = '/home/user/Desktop/git/temp/driving_license/train/images/'

for filename in os.listdir(directory):
    path = os.path.join(directory, filename)
    results = model(path)
    results.crop(save_dir='/home/heli/Desktop/git/demo-site-backend/model_training/notebooks/temp/')
