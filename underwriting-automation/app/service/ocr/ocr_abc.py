import abc

import cv2
import numpy as np


class OCRAbc():
    __metaclass__ = abc.ABCMeta

    async def _apply_preprocessing(self, image):
        original = image
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured1 = cv2.medianBlur(image, 3)
        blured2 = cv2.medianBlur(image, 51)
        divided = np.ma.divide(blured1, blured2).data
        normed = np.uint8(255 * divided / divided.max())
        th, threshed = cv2.threshold(normed, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        image = np.vstack((image, blured1, blured2, normed, threshed))
        return threshed


    async def _apply_red_color_mask(self, image):
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        mask = cv2.inRange(image, (0, 0, 0), (60, 60, 100))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    async def _apply_dark_red_color_mask(self, image):
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        mask = cv2.inRange(image, (0, 0, 0), (80, 85, 98))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    async def _apply_black_color_mask(self, image):
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        mask = cv2.inRange(image, (0, 0, 0), (50, 50, 50))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    async def _apply_gray_color_mask(self, image):
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        mask = cv2.inRange(image, (30, 30, 30), (200, 160, 160))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    async def _apply__dark_gray_color_mask(self, image):
        image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        mask = cv2.inRange(image, (0, 0, 0), (140, 120, 120))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image
