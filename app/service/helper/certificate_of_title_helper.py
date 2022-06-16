import asyncio

import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage import rotate

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
    h, w, _ = image.shape
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
    stack = np.vstack((image, blured1, blured2, normed, image))
    return image


async def text_detection(image, area=6000):
    images = []
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    img = await auto_scale_image(image, resize_dimension=600)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (17, 17), 7)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 3)

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


async def correct_skew(image, delta=1, limit=5):
    def _determine_score(arr, angle):
        data = rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = _determine_score(thresh, angle)
        scores.append(score)
    best_angle = angles[scores.index(max(scores))]
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    mat = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    corrected = cv2.warpAffine(image, mat, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return corrected


async def bradley_roth_numpy(image, s=None, t=None):
    # Convert image to numpy array
    img = np.array(image).astype(float)

    # Default window size is round(cols/8)
    if s is None:
        s = np.round(img.shape[1] / 8)

    # Default threshold is 15% of the total
    # area in the window
    if t is None:
        t = 15.0

    # Compute integral image
    intImage = np.cumsum(np.cumsum(img, axis=1), axis=0)

    # Define grid of points
    (rows, cols) = img.shape[:2]
    (X, Y) = np.meshgrid(np.arange(cols), np.arange(rows))

    # Make into 1D grid of coordinates for easier access
    X = X.ravel()
    Y = Y.ravel()

    # Ensure s is even so that we are able to index into the image
    # properly
    s = s + np.mod(s, 2)

    # Access the four corners of each neighbourhood
    x1 = X - s / 2
    x2 = X + s / 2
    y1 = Y - s / 2
    y2 = Y + s / 2

    # Ensure no coordinates are out of bounds
    x1[x1 < 0] = 0
    x2[x2 >= cols] = cols - 1
    y1[y1 < 0] = 0
    y2[y2 >= rows] = rows - 1

    # Ensures coordinates are integer
    x1 = x1.astype(int)
    x2 = x2.astype(int)
    y1 = y1.astype(int)
    y2 = y2.astype(int)

    # Count how many pixels are in each neighbourhood
    count = (x2 - x1) * (y2 - y1)

    # Compute the row and column coordinates to access
    # each corner of the neighbourhood for the integral image
    f1_x = x2
    f1_y = y2
    f2_x = x2
    f2_y = y1 - 1
    f2_y[f2_y < 0] = 0
    f3_x = x1 - 1
    f3_x[f3_x < 0] = 0
    f3_y = y2
    f4_x = f3_x
    f4_y = f2_y

    # Compute areas of each window
    sums = intImage[f1_y, f1_x] - intImage[f2_y, f2_x] - intImage[f3_y, f3_x] + intImage[f4_y, f4_x]

    # Compute thresholded image and reshape into a 2D grid
    out = np.ones(rows * cols, dtype=bool)
    out[img.ravel() * count <= sums * (100.0 - t) / 100.0] = False

    # Also convert back to uint8
    out = 255 * np.reshape(out, (rows, cols)).astype(np.uint8)

    # Return PIL image back to user
    return out


async def faster_bradley_threshold(img, threshold=75, window_r=5):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    percentage = threshold / 100.
    window_diam = 2 * window_r + 1
    # convert image to numpy array of grayscale values
    # img = np.array(image.convert('L')).astype(np.float)  # float for mean precision
    # matrix of local means with scipy
    means = ndimage.uniform_filter(img, window_diam)
    # result: 0 for entry less than percentage*mean, 255 otherwise
    height, width = img.shape[:2]
    result = np.zeros((height, width), np.uint8)  # initially all 0
    result[img >= percentage * means] = 255  # numpy magic :)
    # convert back to PIL image
    return result
