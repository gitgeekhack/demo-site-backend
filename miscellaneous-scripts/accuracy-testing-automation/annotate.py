import os.path

import cv2
import json
import glob
file_paths = glob.glob('/home/heli/Documents/accuracy/*/**/***/section-classification.json',recursive=True)


def draw_prediction_box(image, prediction):
    bbox = prediction['layout_structure']['bounding_box']
    x1, y1 = int(bbox["x_1"]), int(bbox["y_1"])
    x2, y2 = int(bbox["x_2"]), int(bbox["y_2"])
    label1 = prediction["classified_section"]
    label = str(prediction['layout_structure']['labels'])

    # Draw the rectangle
    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Annotate the label and score
    text = f"{label} {label1}"
    cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)



for path in file_paths:
    with open(path, "r") as file:
        data = json.load(file)

    for pages in data["categorized_document"]["pages"]:
        efs_key = pages["image"]["efs_key"]
        predictions = pages["predictions"]
        image = cv2.imread(f'/home/heli/Documents/accuracy/{efs_key}')

        for prediction in predictions:
            draw_prediction_box(image, prediction)

        cv2.imwrite(f'/home/heli/Documents/accuracy/annotate/{efs_key.replace("/","_")}', image)