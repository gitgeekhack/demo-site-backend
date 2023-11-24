import cv2
from app.constant import Path
from app.common.utils import make_dir


class Annotator:
    def __init__(self, image,coordinates):
        self.image = image
        self.coordinates = coordinates

    def annotate_and_save(self, save_image):
        for co_ord in self.coordinates:
            xmin = int(co_ord[0][0])
            ymin = int(co_ord[0][1])
            xmax = int(co_ord[0][2])
            ymax = int(co_ord[0][3])
            cv2.rectangle(self.image, (xmin, ymin), (xmax, ymax), co_ord[1], 2)
        make_dir(Path.STATIC_PATH + Path.DETECTED_PATH)
        cv2.imwrite(save_image, self.image)
