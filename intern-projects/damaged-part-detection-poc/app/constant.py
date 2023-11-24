import os


class ColorLabels:
    CAR_DAMAGE = {
                "Headlights": (153, 153, 255),
                "Hood": (153, 204, 255),
                "Front Bumper": (153, 255, 255),
                "Rear Bumper": (153, 255, 204),
                "Front Windshield": (153, 255, 153),
                "Rear Windshield": (204, 255, 153),
                "Flat Tyre": (255, 255, 153),
                "Missing Mirror": (255, 204, 153),
                "Missing Wheel": (255, 153, 153),
                "Taillights": (255, 153, 204),
                "Trunk": (255, 153, 255),
                "Window": (204, 153, 255),
                "Door": (224, 2, 224),
                "Fender": (102, 102, 0),
                "Interior Damage": (0, 255, 255)
            }

class Path:
    STATIC_PATH = "app/static/"
    UPLOADED_PATH = "Uploaded/"
    DETECTED_PATH = "Detected/"
    INSTANCE_LOG_FOLDER_PATH = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'logs'))
    YOLOV5 = 'ultralytics/yolov5'
    MODEL_PATH = "./app/models/DamagePartDetection.pt"


class Extension:
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
    PNG = ".png"
    JPG = ".jpg"

