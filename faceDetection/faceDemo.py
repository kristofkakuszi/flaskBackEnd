#futtatás
#python ./faceDetection/face_detection.py --image ./uploads/face.jpg
#ennek kép az inputa


from helpers import convert_and_trim_bb
import argparse
import imutils
import time
import dlib
import cv2

#2 parameteres
# def findFace(image, upsample)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", type=str, required=True,
	help="path to input image")
ap.add_argument("-u", "--upsample", type=int, default=1,
	help="# of times to upsample")
args = vars(ap.parse_args())

# load dlib's HOG + Linear SVM face detector
detector = dlib.get_frontal_face_detector()

# load the input image from disk, resize it, and convert it from
# BGR to RGB channel ordering (which is what dlib expects)
img = cv2.imread(args["image"])
img = imutils.resize(img, width=600)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# perform face detection using dlib's face detector
start = time.time()
rects = detector(rgb, args["upsample"])
end = time.time()


# convert the resulting dlib rectangle objects to bounding boxes,
# then ensure the bounding boxes are all within the bounds of the
# input image
boxes = [convert_and_trim_bb(img, r) for r in rects]
length = 0
# loop over the bounding boxes
for (x, y, w, h) in boxes:
	# draw the bounding box on our image
	cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
length = length + 1

if (length > 0) :
    print("talált")
    #return True
else:
    print("nem talált")


# show the output image
