import os

# data_file consists of 'paths of images' i.e. 'data.yaml'
data_file = './data.yaml'
model_weight = './best.pt'

# command for execute a checkbox evaluation model
os.system(f'python3 val.py --weights {model_weight} --img 640 --data {data_file} --task test')
