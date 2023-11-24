import os
import re

import cv2
import fitz
import numpy as np

path = './data/Source/'
image_path = './images/Signature/'
image_number_on_page = 1


def check_date(block_list):
    flag = False
    for ind, block in enumerate(block_list):
        if block['type'] == 1:
            if ind < len(block_list) - 1 and block_list[ind + 1]['type'] == 0:
                text = block_list[ind + 1]['lines'][0]['spans'][0]['text']
                x = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", text)
                if x:
                    flag = True
    return flag


for root, dirs, files in os.walk(path, topdown=True):
    for file in files:
        filepath = os.path.join(root, file)
        old_pdf = fitz.open(filepath, filetype='pdf')
        pdf_bytes = old_pdf.convert_to_pdf(from_page=0, to_page=old_pdf.page_count)
        new_pdf = fitz.open('pdf', pdf_bytes)
        for page_number in range(len(new_pdf)):
            for image_list in new_pdf.getPageImageList(page_number):
                if image_list and image_list[5] == 'DeviceRGB' and image_list[1]:
                    full_image = fitz.Pixmap(new_pdf, image_list[0])
                    mask = fitz.Pixmap(new_pdf, image_list[1])
                    covered_image = fitz.Pixmap(full_image, mask)
                    np_array = np.asarray(bytearray(covered_image.getImageData()), dtype=np.uint8)
                    input_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
                    trans_mask = input_image[:, :, 3] == 0
                    input_image[trans_mask] = [255, 255, 255, 255]
                    new_img = cv2.cvtColor(input_image, cv2.COLOR_BGRA2BGR)
                    blocks = new_pdf[page_number].getText('dict')['blocks']
                    date = check_date(blocks)
                    if date:
                        cv2.imwrite(image_path + file.split('.')[0] + str(page_number + 1) + '_'
                                    + str(image_number_on_page) + '.png', new_img)

                    else:
                        cv2.imwrite(image_path + file.split('.')[0] + str(page_number + 1) + '_'
                                    + str(image_number_on_page) + '.png', new_img)

                    image_number_on_page += 1
                else:
                    xref = image_list[0]
                    pix = fitz.Pixmap(new_pdf, xref)
                    if pix.n < 5:
                        try:
                            np_array = np.asarray(bytearray(pix.getImageData()), dtype=np.uint8)
                            input_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
                            new_img = cv2.cvtColor(input_image, cv2.COLOR_BGRA2BGR)
                        except Exception as e:
                            cv2.imwrite(image_path + file.split('.')[0] + str(page_number + 1) + '_'
                                        + str(image_number_on_page) + '.png', input_image)
                        cv2.imwrite(image_path + file.split('.')[0] + str(page_number + 1) + '_'
                                    + str(image_number_on_page) + '.png', new_img)
                        image_number_on_page += 1
                    else:
                        pix1 = fitz.Pixmap(fitz.csRGB, pix)
                        np_array = np.asarray(bytearray(pix1.getImageData()), dtype=np.uint8)
                        input_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
                        new_img = cv2.cvtColor(input_image, cv2.COLOR_BGRA2BGR)
                        cv2.imwrite(image_path + file.split('.')[0] + str(page_number + 1) + '_'
                                    + str(image_number_on_page) + '.png', new_img)
                        image_number_on_page += 1
                    pix = None
            image_number_on_page = 1
