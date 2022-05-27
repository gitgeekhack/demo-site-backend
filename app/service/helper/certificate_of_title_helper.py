import asyncio

import cv2
import numpy as np

from app.business_rule_exception import MissingRequiredParameter
from app.service.helper.cv_helper import CVHelper


class COTHelper(CVHelper):

    async def get_skew_angel(self, extracted_objects):
        find_skew_angles = [self._calculate_skew_angel(extracted_object['detected_object']) for
                            extracted_object in extracted_objects]
        skew_angles = await asyncio.gather(*find_skew_angles)
        skew_angle = np.mean(skew_angles)
        return skew_angle


async def image_resize(image, width=None, height=None, interpolation=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    resized = cv2.resize(image, dim, interpolation=interpolation)
    return resized


async def auto_scale_image(image, resize_dimension=500):
    h, w, c = image.shape
    if resize_dimension:
        if w > h:
            image = await image_resize(image, width=resize_dimension, height=None, interpolation=cv2.INTER_CUBIC)
        else:
            image = await image_resize(image, width=None, height=resize_dimension, interpolation=cv2.INTER_CUBIC)
    return image


async def apply_preprocessing(image, auto_scaling=False, resize_dimension=None):
    if auto_scaling and resize_dimension:
        image = await auto_scale_image(image, resize_dimension=resize_dimension)
    if auto_scaling and not resize_dimension or not auto_scaling and resize_dimension:
        raise MissingRequiredParameter(message='Missing Required input Parameter for Image auto scaling')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blured1 = cv2.medianBlur(image, 3)
    blured2 = cv2.medianBlur(image, 51)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255 * divided / divided.max())
    th, image = cv2.threshold(normed, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    image = cv2.erode(image, np.ones((3, 3), np.uint8))
    image = cv2.dilate(image, np.ones((3, 3), np.uint8))
    return image


async def text_detection(image, area=6000):
    images = []
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    img = await auto_scale_image(image, resize_dimension=600)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (17, 17), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 3)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 4))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    for c in contours:
        cnt_area = cv2.contourArea(c)
        if cnt_area > area:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 2)
            roi = img[y:y + h, x:x + w]
            images.append(roi)

    return images


async def noise_removal(image):
    h, w = image.shape[:2]
    # Ensure only bi-level image with white as foreground
    _, bi_img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
    # Add one pixel border
    bi_img = cv2.copyMakeBorder(bi_img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, None, 255)
    # Extract connected components (Spaghetti is the fastest algorithm)
    n_labels, label_image = cv2.connectedComponentsWithAlgorithm(bi_img, 8, cv2.CV_32S, cv2.CCL_SPAGHETTI)
    # Make a mask with the edge label (0 is background, 1 is the first encountered label, i.e. the border)
    cc_edge = np.uint8((label_image != 1) * 255)
    # Zero every pixel touching the border
    bi_img = cv2.bitwise_and(bi_img, cc_edge)
    # Remove border and invert again
    bi_img = 255 - bi_img[1:h + 1, 1:w + 1]
    return bi_img
