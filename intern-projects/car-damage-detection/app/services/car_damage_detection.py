from ultralytics import YOLO
from flask import render_template
import os
import cv2
from app.constants import Path


class ObjectDetector:
    _shared_state = {}

    def __init__(self, model_path):
        self.__dict__ = self._shared_state
        if not self._shared_state:
            self.model = YOLO(Path.MODEL_PATH)

    def detect_objects(self, image_path):
        results = self.model(image_path)
        res_plotted = results[0].plot()
        resized_image = cv2.resize(res_plotted, (640, 480))
        return resized_image, results


detector = ObjectDetector(Path.MODEL_PATH)


def predict(request):
    try:
        files = request.files.getlist('file')
        if not files:
            error = 'No files were uploaded'
            return render_template('index.html', error=error)

        predict_img_list = []
        class_label_list = []
        for file in files:
            # Save the file to the uploads folder
            file_path = os.path.join(Path.UPLOAD_PATH, file.filename)
            file.save(file_path)

            # Perform object detection on the uploaded file
            save_path = os.path.join(Path.PREDICT_PATH, file.filename)
            predict_img_list.append(file.filename)
            resized_image, results = detector.detect_objects(file_path)

            # Save the resized image to a file
            cv2.imwrite(save_path, resized_image)

            # Get the labels and confidence scores for the detected objects
            label_conf_dict = {}
            for result in results:
                for index in range(len(result.boxes)):
                    label = detector.model.names[int(result.boxes.cls[index])]
                    label = label.replace('_', ' ')
                    label = label.title()
                    conf = float(result.boxes.conf[index])
                    if label in label_conf_dict:
                        label_conf_dict[label].append(conf * 100)
                    else:
                        label_conf_dict[label] = [conf * 100]

            class_conf_dict = {}  # create a new dictionary for class-confidence mapping
            for label, conf_list in label_conf_dict.items():
                class_conf_dict[label] = max(conf_list)

            # Append the results to the list of all results
            class_label_list.append(class_conf_dict)

        # Pass the paths of the original and predicted images to the HTML template
        return render_template('predict.html', base_name=predict_img_list, dict=class_label_list)

    except IsADirectoryError:
        error = 'oops!! no file uploaded. Please upload JPG, JPEG or PNG files.'
        return render_template('index.html', error=error)

    except Exception as e:
        error = f'An error occurred: {str(e)}'
        return render_template('index.html', error=error)

