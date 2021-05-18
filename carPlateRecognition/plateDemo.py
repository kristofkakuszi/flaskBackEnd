from carPlateRecognition.license import PyImageSearchANPR
from imutils import paths
import argparse
import imutils
import cv2

def cleanup_text(text):
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()

def findPlate(input, clear_border=1, psm=7, debug=-1):

	anpr = PyImageSearchANPR(debug=debug > 0)

	image = cv2.imread(input)
	image = imutils.resize(image, width=600)

	(lpText, lpCnt) = anpr.find_and_ocr(image, psm=psm,
		clearBorder=clear_border > 0)

	if lpText is not None and lpCnt is not None:

		box = cv2.boxPoints(cv2.minAreaRect(lpCnt))
		box = box.astype("int")
		cv2.drawContours(image, [box], -1, (0, 255, 0), 2)

		(x, y, w, h) = cv2.boundingRect(lpCnt)
		cv2.putText(image, cleanup_text(lpText), (x, y - 15),
			cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
		print("van rendszam")
		return True
	else:
		print("nincs rendszam")
		return False
