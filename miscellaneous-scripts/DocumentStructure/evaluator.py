import os

images_folder = "/home/ubuntu/git/pareit-miscellaneous-scripts/checkbox_mark_detection/cropped_section_images/"
NUM_GPU = 4
BATCH_PER_IMAGE = 128
CHECKPOINT = 100
MAX_ITERATION = 3000
IMAGES_PER_BATCH = 4
UNSEEN_TEST_JSON = ''
UNSEEN_TEST_IMAGE = ''
CONFIGURATION_FILE_PATH = "./config.yaml"
MODEL_PATH = "/home/ubuntu/git/pareit-miscellaneous-scripts/checkbox_mark_detection/model_final.pth"
OUTPUT_DIR = "/home/ubuntu/git/pareit-miscellaneous-scripts/checkbox_mark_detection/detectron2_results/"

os.system(
    f"""python3 train_net.py --dataset_name "my_dataset" --eval-only --json_annotation_train "" --image_path_train "{images_folder}/" --json_annotation_val {UNSEEN_TEST_JSON} --image_path_val {UNSEEN_TEST_IMAGE} --config-file {CONFIGURATION_FILE_PATH} --num-gpus {NUM_GPU}  MODEL.WEIGHTS {MODEL_PATH} OUTPUT_DIR {OUTPUT_DIR} MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE {BATCH_PER_IMAGE} SOLVER.CHECKPOINT_PERIOD {CHECKPOINT} SOLVER.MAX_ITER {MAX_ITERATION} SOLVER.IMS_PER_BATCH {IMAGES_PER_BATCH}""")
