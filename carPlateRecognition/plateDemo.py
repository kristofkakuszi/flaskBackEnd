from carPlateRecognition.license import PyImageSearchANPR
from imutils import paths
import argparse
import imutils
import cv2

def cleanup_text(text):
	# strip out non-ASCII text so we can draw the text on the image
	# using OpenCV
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()

def findPlate(input, clear_border=1, psm=7, debug=-1):

	# initialize our ANPR class
	anpr = PyImageSearchANPR(debug=debug > 0)

	# grab all image paths in the input directory

	#length = 0
	# loop over all image paths in the input directory

	# load the input image from disk and resize it
	image = cv2.imread(input)
	image = imutils.resize(image, width=600)

	# apply automatic license plate recognition
	(lpText, lpCnt) = anpr.find_and_ocr(image, psm=psm,
		clearBorder=clear_border > 0)

	lpCounter = 0

	# only continue if the license plate was successfully OCR'd
	if lpText is not None and lpCnt is not None:
		# fit a rotated bounding box to the license plate contour and
		# draw the bounding box on the license plate
		lpCounter = lpCounter + 1
		box = cv2.boxPoints(cv2.minAreaRect(lpCnt))
		box = box.astype("int")
		cv2.drawContours(image, [box], -1, (0, 255, 0), 2)

		# compute a normal (unrotated) bounding box for the license
		# plate and then draw the OCR'd license plate text on the
		# image
		(x, y, w, h) = cv2.boundingRect(lpCnt)
		cv2.putText(image, cleanup_text(lpText), (x, y - 15),
			cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
		# show the output ANPR image
		if (lpCounter > 0) :
			print("talált rendszámtáblát")
			return True
		else:
			print("nem talált rendszámtáblát")
			return False
