import os


images_folder = "LONG_PAGES_TEMP"
num_gpus = 4
batch_per_image = 512
checkpoint_period = 10000
max_iter = 30000
n_folds = 10
ims_per_batch = 4
for i in range(n_folds):
    os.system(
        f"""python train_net.py --dataset_name "my_dataset" --json_annotation_train "DATASET/train_{i}.json" --image_path_train "{images_folder}/" --json_annotation_val "DATASET/test_{i}.json" --image_path_val "{images_folder}/" --config-file "publay_model/config.yaml" --num-gpus {num_gpus}  MODEL.WEIGHTS "publay_model/model_final.pth" OUTPUT_DIR "finetuned_model_{i}_lp" MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE {batch_per_image} SOLVER.CHECKPOINT_PERIOD {checkpoint_period} SOLVER.MAX_ITER {max_iter} SOLVER.IMS_PER_BATCH {ims_per_batch}"""
    )
