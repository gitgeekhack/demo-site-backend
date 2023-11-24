# from app.darknet import darknet
#
#
# imagePath = "darknet/44544089_2.jpg"
# configPath = "darknet/cfg/yolov3-obj.cfg"
# weightPath = "darknet/yolov3-obj_best.weights"
# metaPath = "darknet/data/obj.data"
# print(darknet.performDetect(initOnly=True, configPath=configPath, weightPath=weightPath, metaPath=metaPath))
# print(darknet.performDetect(imagePath=imagePath, configPath=configPath, weightPath=weightPath, metaPath=metaPath))

from app import app

if __name__ == '__main__':
    app.run('0.0.0.0')