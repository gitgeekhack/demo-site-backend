import os
import shutil
from os import listdir
from os.path import isfile, join

import numpy as np

source = '../../data/Signature/RAW/'
target = '../../data/Signature/dataset/'
class_label1 = 'Signature'
class_label2 = 'No_Signature'


def make_dir(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def copy_files(source_dir, split_label, class_label, files):
    for file in files:
        make_dir(join(target, split_label, class_label))
        shutil.copy(join(source_dir, class_label, file), join(target, split_label, class_label, file))


def get_files(source_path, lable):
    return np.array([f for f in listdir(join(source_path, lable)) if isfile(join(source_path, lable, f))])


def split_data(array, test_ratio, valid_ratio):
    return np.split(array, [int(valid_ratio * len(array)), int((valid_ratio + test_ratio) * len(array))])


signature = get_files(source, lable=class_label1)
no_signature = get_files(source, lable=class_label2)

np.random.shuffle(signature)
np.random.shuffle(no_signature)

signature_valid, signature_test, signature_train = split_data(signature, 0.15, 0.15)
no_signature_valid, no_signature_test, no_signature_train = split_data(no_signature, 0.15, 0.15)

copy_files(source_dir=source, split_label='train', class_label=class_label1, files=signature_train)
copy_files(source_dir=source, split_label='test', class_label=class_label1, files=signature_test)
copy_files(source_dir=source, split_label='valid', class_label=class_label1, files=signature_valid)
copy_files(source_dir=source, split_label='train', class_label=class_label2, files=no_signature_train)
copy_files(source_dir=source, split_label='test', class_label=class_label2, files=no_signature_test)
copy_files(source_dir=source, split_label='valid', class_label=class_label2, files=no_signature_valid)
