"""This Program contains Preprocessing steps and Object Detection"""

import imutils
import cv2
import numpy
import numpy as np
from PIL import Image, ImageEnhance
from pyzbar import pyzbar
import io
import traceback
import fitz
from PIL import Image
from app.common.utils import stop_watch
from flask import current_app
from app.business_rule_exception import InvalidFileException

class ImageHelper:

    @stop_watch
    def __morphing(self, image):
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        eroded = cv2.erode(closed, kernel)
        eroded = cv2.erode(eroded, kernel)
        dilated = cv2.dilate(eroded, kernel)
        dilated = cv2.dilate(dilated, kernel)
        return dilated

    @stop_watch
    def __sharpening(self, image, kernel_size=(9, 9), sigma=1.0, amount=1.0, threshold=0):
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    @stop_watch
    def __resizing(self, image, n):
        h = 300 * n
        w = 400 * n
        if image.shape[0] > h or image.shape[1] > w:
            image = imutils.resize(image, height=h, width=w, inter=cv2.INTER_AREA)
        return image

    @stop_watch
    def __enhance_contrast(self, image, factor=1.5):
        color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(color_coverted)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(factor)
        opencvImage = cv2.cvtColor(numpy.array(enhanced_image), cv2.COLOR_RGB2BGR)
        return opencvImage

    @stop_watch
    def __denoising(self, image, sigma=20):
        dst = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, sigma)
        return dst

    @stop_watch
    def __grayscale(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    @stop_watch
    def __edge_detection(self, image):
        gradX = cv2.Sobel(image, cv2.CV_8UC1, 1, 0, ksize=3)
        gradY = cv2.Sobel(image, cv2.CV_8UC1, 0, 1, ksize=3)
        subtract = cv2.subtract(gradX, gradY)
        return subtract

    @stop_watch
    def __blur_threshold(self, image, kernel=(9, 9)):
        blur = cv2.GaussianBlur(image, kernel, 0)
        th, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
        return thresh

    @stop_watch
    def __contour_finding(self, image):
        cnts = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            c = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
            return c
        return False

    @stop_watch
    def __crop_box(self, image, c):
        rect = cv2.minAreaRect(c)
        box = np.int0(cv2.boxPoints(rect))
        y1 = box[0][1] - 130
        y2 = box[2][1] + 100
        if y1 > y2:
            yn = y1
            y = y2
        else:
            y = y1
            yn = y2
        new_image = image[y:yn, ]
        if new_image.shape[0] <= 0 or new_image.shape[1] <= 0:
            return image
        return new_image

    @stop_watch
    def preprocess(self, image):
        image = self.__resizing(image, 4)
        image = self.__sharpening(image)
        image = self.__enhance_contrast(image)
        image = self.__denoising(image)
        return image

    @stop_watch
    def object_detection(self, image):
        raw_image = image
        image = self.__grayscale(image)
        image = self.__edge_detection(image)
        image = self.__blur_threshold(image)
        image = self.__morphing(image)
        c = self.__contour_finding(image)
        if c is not False:
            image = self.__crop_box(raw_image, c)
            image = self.__denoising(image, sigma=30)
        return image

