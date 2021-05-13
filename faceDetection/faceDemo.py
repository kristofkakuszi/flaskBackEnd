#futtatás
#python ./faceDetection/face_detection.py --image ./uploads/face.jpg
#uploads\1\7491ab50-ea3d-49ed-8127-0098ec7eeabd.jpg
#ennek kép az inputa
import os

from faceDetection.helpers import convert_and_trim_bb
import imutils
import time
import dlib
import cv2

def findFace(image, upsample=1):

	# load dlib's HOG + Linear SVM face detector
	detector = dlib.get_frontal_face_detector()

	# load the input image from disk, resize it, and convert it from
	# BGR to RGB channel ordering (which is what dlib expects)
	img = cv2.imread(image)
	img = imutils.resize(img, width=600)
	rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

	rects = detector(rgb, upsample)

	boxes = [convert_and_trim_bb(img, r) for r in rects]
	length = 0
	# loop over the bounding boxes
	for (x, y, w, h) in boxes:
		# draw the bounding box on our image
		cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
	length = length + 1
	if (length > 0) :
		print("talált arcot")
		return True
	else:
		print("nem talált arcot")
		return False

# show the output image
