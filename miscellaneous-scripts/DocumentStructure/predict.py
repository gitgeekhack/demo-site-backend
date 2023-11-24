import os
import pathlib

import cv2
import layoutparser as lp
import asyncio
from detectron2.data import MetadataCatalog

REQUIRED_LABELS = ['TITLE', 'SUBTITLE', 'CONTENT', 'FORM', 'HEADER_FOOTER', 'OTHER', 'TABLE']  # labels to be prediction
LABELS_WITH_COLORS = {'TITLE': (255, 0, 0), 'SUBTITLE': (0, 255, 0),
                      'CONTENT': (0, 0, 255)}  # dictionary mapping for labels and respective colors
LABEL_MAP = {0: 'TITLE', 1: 'SUBTITLE', 2: 'CONTENT', 3: 'FORM', 4: 'HEADER_FOOTER', 5: 'OTHER',
             6: 'TABLE'}  # label encoding
EVALUATION_MODEL_PATH = './layout_model/model_final.pth'  # Model path
EVALUATION_CONFIG_PATH = './layout_model/config.yaml'  # Model configuration path
PRIMARY_LABEL_CATEGORY = ['TITLE', 'SUBTITLE', 'CONTENT', 'FORM', 'HEADER_FOOTER', 'OTHER', 'TABLE']  # all labels
THRESHOLD = 0.7
path = ''  # filepath to the image to be predicted

layout_model = lp.Detectron2LayoutModel(EVALUATION_CONFIG_PATH, EVALUATION_MODEL_PATH,
                                        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", THRESHOLD],
                                        label_map=LABEL_MAP)

v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
out = v.draw_instance_predictions(outputs["instances"].to("cpu"))


async def predict_layout(image, save=False):
    layout_model.detect(image)
    layout = layout_model.detect(image)
    predicted_layout = [{'label': i.type, 'score': i.score, 'x_1': i.block.x_1, 'y_1': i.block.y_1, 'x_2': i.block.x_2,
                         'y_2': i.block.y_2} for i in layout if i.type in REQUIRED_LABELS]
    if save:
        await save_annotate_layout(image, predicted_layout)
    return predicted_layout


async def save_annotate_layout(image, predicted_layout):
    for predict in predicted_layout:
        cv2.rectangle(image, pt1=(int(predict['x_1']), int(predict['y_1'])),
                      pt2=(int(predict['x_2']), int(predict['y_2'])), color=LABELS_WITH_COLORS[predict['label']],
                      thickness=2)
    cv2.imwrite(os.path.basename(path), image)


async def visualise():
    v = Visualizer(im[:, :, ::-1], metadata=train_metadata, scale=0.8, )
    for box in outputs["instances"].pred_boxes.to('cpu'):
        v.draw_box(box)
        v.draw_text(str(box[:2].numpy()), tuple(box[:2].numpy()))
    v = v.get_output()
    img = v.get_image()[:, :, ::-1]
    cv2_imshow(img)


async def main():
    image = cv2.imread(path)
    predicted_layout = await predict_layout(image)
    print(predicted_layout)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
