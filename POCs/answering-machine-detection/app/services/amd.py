"""
AMD signifies Answering Machine Detection service which contains predictor class.
The overall aim of the class is to predict the nature of the audio,if the audio is a Human Audio or a Non-Human Audio.
"""
import numpy as np

from app import pipe_line, MODEL


class BinaryPredictor:
    """
    This class returns the classified prediction of the input audio from the AMD model.
    """

    async def predict(self, file):
        """
        Parameter:
            file: The input audio file.

        Return:
            prediction: prediction label from the Model output.
        """
        tensor, audio_length = await pipe_line.pre_process(file)
        y_pred = MODEL.predict(tensor)
        prediction = np.argmax(y_pred, axis=-1)[0]
        return prediction, audio_length
