import asyncio

import cv2
import numpy as np
from scipy.ndimage import interpolation as inter


class CVHelper:

    async def get_object(self, target_img, coordinates, label):
        """
        Parameters:
            target_img <class 'numpy.ndarray'>: The target image which is to be cropped.
            coordinates <class 'list'>: The coordinates of the region to be cropped, a 4-element list containing
                                of x/y (x0, y0, x1, y1) pixel coordinates.
        Returns:
            cropped_img <class 'numpy.ndarray'>: The final image which is cropped with the coordinates provided.
        """
        x0, y0, x1, y1 = [int(x) for x in coordinates]
        w = target_img.shape[0]
        h = target_img.shape[1]
        padd = 0.005
        w_padd = w * padd
        h_padd = h * padd
        x0, y0 = int(x0 - w_padd), int(y0 - w_padd)
        x1, y1 = int(x1 + h_padd), int(y1 + h_padd)
        cropped_img = target_img[y0:y1, x0:x1]
        return {'detected_object': cropped_img, 'label': label}

    async def calculate_iou(self, x, y):
        x0 = max(x[0], y[0])
        y0 = max(x[1], y[1])
        x1 = min(x[2], y[2])
        y1 = min(x[3], y[3])
        inter_area = max(0, x1 - x0 + 1) * max(0, y1 - y0 + 1)
        box0_area = (x[2] - x[0] + 1) * (x[3] - x[1] + 1)
        box1_area = (y[2] - y[0] + 1) * (y[3] - y[1] + 1)
        iou = inter_area / float(box0_area + box1_area - inter_area)
        return iou

    async def _find_skew_score(self, arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
        return histogram, score

    async def _calculate_skew_angel(self, image, delta=5, limit=45):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        scores = []
        angles = np.arange(-limit, limit + delta, delta)
        for angle in angles:
            histogram, score = await self._find_skew_score(thresh, angle)
            scores.append(score)
        best_angle = angles[scores.index(max(scores))]
        return best_angle

    async def get_skew_angel(self, extracted_objects):
        find_skew_angles = [self._calculate_skew_angel(extracted_object['detected_object']) for
                            extracted_object in extracted_objects]
        skew_angles = await asyncio.gather(*find_skew_angles)
        max_skew_angle = np.max(skew_angles)
        min_skew_angle = np.min(skew_angles)
        if min_skew_angle < 0:
            skew_angle = min_skew_angle
        else:
            skew_angle = max_skew_angle

        return skew_angle

    async def fix_skew(self, image, angle):
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    async def automatic_enhancement(self, image, clip_hist_percent=1):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_size = len(hist)
        accumulator = [float(hist[0])]
        for index in range(1, hist_size):
            accumulator.append(accumulator[index - 1] + float(hist[index]))
        maximum = accumulator[-1]
        clip_hist_percent *= (maximum / 100.0)
        clip_hist_percent /= 2.0
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1
        maximum_gray = hist_size - 1
        while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
            maximum_gray -= 1
        # Calculate alpha and beta values
        alpha = 255 / (maximum_gray - minimum_gray)
        beta = -minimum_gray * alpha

        '''
        # Calculate new histogram with desired range and show histogram 
        new_hist = cv2.calcHist([gray], [0], None, [256], [minimum_gray, maximum_gray])
        plt.plot(hist)
        plt.plot(new_hist)
        plt.xlim([0, 256])
        plt.show()
    
        '''
        auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return auto_result
