import inspect
from datetime import datetime

import tensorflow as tf
from tensorflow.keras.models import load_model

from constants import MODEL_PATH
img_size = 150


def stop_watch(f):
    """The method provides execution time of the method it is used upon."""

    def timer(*args, **kwargs):
        start = datetime.now()
        x = f(*args, **kwargs)
        end = datetime.now()
        diff = end - start
        diff = diff.microseconds / 1000
        print(f'{args[1]} => {x:>12} | Took: [{diff:>7}] ms')
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

    @stop_watch
    def classify(self, path):
        data = self.__preprocess(path)
        result = "Signature" if self.model.predict(data) > 0 else "No_Signature"
        return result


classifier = SignatureClassifier()
test_list = []
+\

    classifier.classify('./sample/VER_PTP_Armanza Santacruz, Maria1_3.png')
