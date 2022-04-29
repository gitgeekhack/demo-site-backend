import os

import cv2
from OCR.driving_license.ocr import OCRDrivingLicense

directory = '/home/heli/Desktop/git/temp/test'
ocr_object = OCRDrivingLicense()
for filename in os.listdir(directory):
    path = os.path.join(directory, filename)
    img = cv2.imread(path)

    text = ocr_object.get_license_number(img)
    print(text)

    cv2.imshow('',img)
    cv2.waitKey()