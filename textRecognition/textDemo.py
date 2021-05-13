#futtatás
#python textRecognition/textDetection.py --image ./uploads/sign.jpg --east textRecognition/frozen_east_text_detection.pb

#ennek kép az inputa

from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import time
import cv2
import os

def findText(image, min_confidence=0.5, width=320, height=320):

    east = os.path.join(os.path.dirname(__file__),"frozen_east_text_detection.pb")
    print(east)

    img = cv2.imread(image)
    orig = img.copy()
    (H, W) = img.shape[:2]

    (newW, newH) = (width, height)
    rW = W / float(newW)
    rH = H / float(newH)

    img = cv2.resize(img, (newW, newH))
    (H, W) = img.shape[:2]

    layerNames = [
        "feature_fusion/Conv_7/Sigmoid",
        "feature_fusion/concat_3"]

    net = cv2.dnn.readNet(east)

    blob = cv2.dnn.blobFromImage(img, 1.0, (W, H),
                                 (123.68, 116.78, 103.94), swapRB=True, crop=False)

    net.setInput(blob)
    (scores, geometry) = net.forward(layerNames)

    (numRows, numCols) = scores.shape[2:4]
    rects = []
    confidences = []

    for y in range(0, numRows):

        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        for x in range(0, numCols):

            if scoresData[x] < min_confidence:
                continue

            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]


            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    boxes = non_max_suppression(np.array(rects), probs=confidences)
    length = 0

    for (startX, startY, endX, endY) in boxes:

        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)
        length = length + 1

    if (length > 0) :
        print("talált szöveget")
        return True
    else:
        print("nem talált szöveget")
        return False