import tensorflow as tf
import numpy as np
from app.common.utils import MonoState
import tensorflow_hub as hub
from app.constant import MOBILENET_V2_URL


def load_module():
    module_handle = MOBILENET_V2_URL
    return hub.load(module_handle)


class FeatureExtraction(MonoState):
    _internal_state = {"module": load_module()}

    def load_image(self, image_path):
        """
        function for loading single image and applying preprocessing
        Parameters:
            image_path <string>: path of an image to load
        Returns:
            img <Tensor>: image tensor of shape [1, 224, 224, 3]
        """
        img = tf.io.read_file(image_path)

        img = tf.io.decode_jpeg(img, channels=3)

        img = tf.image.resize_with_pad(img, 224, 224)

        # Resizing image to input dimension required for "mobilenetv2" model
        img = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]

        return img

    def getvectors(self, filenames):
        """
        function for generating feature vectors of given files
        Parameters:
            filenames <list>: list of filepaths
        Returns:
            vectors <list>: list of vectors generated
        """
        vectors = []
        for filename in filenames:
            img = self.load_image(filename)
            features = self.module(img)
            feature_vector = np.squeeze(features)
            vectors.append(feature_vector)
        return vectors
