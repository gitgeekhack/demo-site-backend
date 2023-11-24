import os
from datetime import datetime

import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model

from constants import MODEL_PATH

# target = '../../data/Signature/dataset/test/'
target = './test_imgs/'
master_list = []

img_size = 150


def stop_watch(f):
    """The method provides execution time of the method it is used upon."""

    def timer(*args, **kwargs):
        start = datetime.now()
        x = f(*args, **kwargs)
        end = datetime.now()
        diff = end - start
        diff = diff.microseconds / 1000
        print(f'{args[1].replace("./test_imgs/", ""):<30} => {x:>12} | Took: {diff:>7} ms')
        return x

    return timer


class SignatureClassifier:

    def __init__(self):
        self.model = load_model(MODEL_PATH)

    def __preprocess(self, path):
        img = tf.keras.utils.load_img(path, target_size=(150, 150))
        img_array = tf.keras.utils.img_to_array(img) / 255
        img_array = tf.expand_dims(img_array, 0)
        return img_array

    # @stop_watch
    def classify(self, path):
        data = self.__preprocess(path)
        result = "Signature" if self.model.predict(data) > 0 else "No_Signature"
        return result


classifier = SignatureClassifier()
test_list = []
for root, dirs, files in os.walk(target):
    for dir in dirs:
        for _, _, files in os.walk(os.path.join(target, dir)):
            for file in files:
                path = os.path.join(target, dir, file)
                actual = dir
                test_list.append([path, actual])
from tqdm import tqdm

for i in tqdm(test_list, desc='Testing images'):
    path = i[0]
    actual = i[1]
    predict = classifier.classify(path)
    is_accurate = True if actual == predict else False
    data = [path, actual, predict, is_accurate]
    master_list.append(data)

df = pd.DataFrame(master_list, columns=['file', 'Actual', 'Predicted', 'Is-True'])
df.to_csv('prediction.csv', index=False)
