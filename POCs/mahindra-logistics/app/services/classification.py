import cv2
import numpy as np
from app.common.utils import stop_watch


class Classification:

    @stop_watch
    def __create_npy(self, image):
        data = []
        size = (480, 480)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, size)
        data.append(image)
        data = np.array(data, dtype=np.float32) / 255.0
        return data

    @stop_watch
    def classify(self, image):
        from app import Model
        data = self.__create_npy(image)
        forecast = Model.predict(data)
        value = np.argmax(forecast)
        label_collection = {
            0: "Clear",
            1: "Invalid",
            2: "Unclear",
        }
        return label_collection.get(value)
