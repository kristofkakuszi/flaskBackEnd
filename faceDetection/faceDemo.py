import cv2
import dlib
import imutils

from faceDetection.helpers import convert_and_trim_bb


def findFace(image, upsample=1):

	detector = dlib.get_frontal_face_detector()

	img = cv2.imread(image)
	img = imutils.resize(img, width=600)
	rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

	rects = detector(rgb, upsample)

	boxes = [convert_and_trim_bb(img, r) for r in rects]


	for (x, y, w, h) in boxes:
		cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

	if not boxes:
		print("nincs arc")
		return False
	else:
		print("van arc")
		return True

