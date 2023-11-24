import tensorflow as tf
from tensorflow.keras.models import load_model

from app.common.utils import MonoState
from app.constant import Signature
from app.service.helper.cv_helper import CVHelper


def model_loader():
    model = load_model(Signature.SIGNATURE_VERIFIER_MODEL_PATH)
    return model


class ValidateSignatureV1(MonoState):
    _internal_state = {'model': model_loader()}

    async def __pre_process(self, image):
        image = tf.image.resize(image, [Signature.IMG_SIZE, Signature.IMG_SIZE])
        img_array = tf.keras.utils.img_to_array(image) / 255
        img_array = tf.expand_dims(img_array, 0)
        return img_array

    async def _is_signature(self, image):
        data = await self.__pre_process(image)
        return True if self.model.predict(data) > Signature.FORECAST_THRESHOLD else False

    async def validate(self, doc, section_bbox, images, page):
        result = False
        cv_helper = CVHelper()
        for img in images:
            result_iou = await cv_helper.calculate_iou(section_bbox, page.get_image_bbox(img))
            if result_iou > 0:
                image_data = await cv_helper.extract_image_from_pdf(doc, img)
                result = await self._is_signature(image_data)
                return result
        return result
