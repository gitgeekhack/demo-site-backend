import cv2
import torch
from app.constant import Path
from app.common.utils import MonoState
from app.services.helpers.cv_helper import Annotator
from app.constant import ColorLabels


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(Path.YOLOV5, 'custom', path=Path.MODEL_PATH)
    model.conf = 0.49
    return model


class DamageDetect(MonoState):
    _internal_state = {'model': model_loader()}

    def annotate(self, image, co_ordinates, save_path):
        annotator = Annotator(image, co_ordinates)
        annotator.annotate_and_save(save_path)

    def label_colour(self, key):
        return ColorLabels.CAR_DAMAGE[key]

    def predict_labels(self, image, save_path):
        labels = []
        results = self.model(image)
        pred = results.pred
        all_labels = results.names
        for p in pred:
            img_res = tuple(map(tuple, p.numpy()))
            labels = [[x, 0] for x in all_labels]
            co_ordinates = [[res[:4], self.label_colour(all_labels[int(res[-1])])] for res in img_res]
            for label in labels:
                for res in img_res:
                    if all_labels[int(res[-1])] == label[0]:
                        label[1] = int(res[4] * 100)
            img = cv2.imread(image)
            self.annotate(img, co_ordinates, save_path)
        return labels

    def detect(self,images):
        results = []
        image_count = 1

        for image in images.split(','):
            image_path = Path.STATIC_PATH + Path.UPLOADED_PATH + image
            output_path = Path.STATIC_PATH + Path.DETECTED_PATH + 'out_' + image
            detection = self.predict_labels(image_path, output_path)
            out_path = Path.DETECTED_PATH + 'out_' + image
            results.append({'image_path': out_path, 'detection': detection, 'image_count': image_count})
            image_count += 1
        return results
