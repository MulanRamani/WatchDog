# USAGE
# python recognize_faces_video.py --encodings encodings.pickle
# python recognize_faces_video.py --encodings encodings.pickle --output output/jurassic_park_trailer_output.avi --display 0

# import the necessary packages
from imutils.video import VideoStream
import os
import glob
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import datetime
import re

THIS_PATH = os.path.dirname(os.path.realpath(__file__))
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")
pathdir = os.path.join(THIS_PATH,'picsfromcam/'+today)

def get_id(name):
	try:
		id = name.split('_')[1][:-4]
		id = ''.join(id)
		return int(id)
	except:
		raise Exception('Problem with {}'.format(name))

if os.path.isdir(pathdir) == False:
	os.mkdir(pathdir)
	counter_global = 0
else:
	listfiles = glob.glob(os.path.join(pathdir,'*.jpg'))
	names = [os.path.basename(os.path.normpath(path)) for path in listfiles]
	ids = [get_id(name) for name in names if 'face' not in name]
	if len(ids)>0:
		counter_global = max(ids)
	else:
		counter_global = 0
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-tpic", "--timepic", type=float,default=0.0,
	help="time between pictures while bursting, in seconds")
ap.add_argument("-b", "--burst", type=int, default=20,
	help="number of pics in burst")
ap.add_argument("-tsleep", "--timesleep", type=float, default=10.0,
	help="time between bursts")

ap.add_argument("-tol", "--tolerance", type=float, default=0.6,
	help="tolerance for comparing faces")


args = vars(ap.parse_args())

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
writer = None
time.sleep(2.0)
counter = 0
# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()

	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	#rgb = imutils.resize(frame, width=1500)
	r = frame.shape[1] / float(rgb.shape[1])

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
	boxes = face_recognition.face_locations(rgb,
		model='hog')
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []
	if len(boxes)>0:
		print('face detected')
		image_name = os.path.join(pathdir,today+'_'+str(counter_global)+'.jpg')
		cv2.imwrite(image_name,frame)

		for (j,(top, right, bottom, left)) in enumerate(boxes):
			encoding = encodings[j]

			matches = face_recognition.compare_faces(data["encodings"],
				encoding,tolerance=args['tolerance'])
			name = "Unknown"

			# check to see if we have found a match
			if True in matches:
				# find the indexes of all matched faces then initialize a
				# dictionary to count the total number of times each face
				# was matched
				matchedIdxs = [i for (i, b) in enumerate(matches) if b]
				counts = {}

				# loop over the matched indexes and maintain a count for
				# each recognized face face
				for i in matchedIdxs:
					name = data["names"][i]
					counts[name] = counts.get(name, 0) + 1

				# determine the recognized face with the largest number
				# of votes (note: in the event of an unlikely tie Python
				# will select first entry in the dictionary)
				name = max(counts, key=counts.get)


			face = frame[top:bottom,left:right]
			face_name = os.path.join(pathdir,today+'_'+str(counter_global)+'_face_'+name+'_'+str(j)+'.jpg')
			cv2.imwrite(face_name,face)


		counter_global += 1
		counter += 1
		time.sleep(args['timepic'])
	if counter > args['burst']:
		time.sleep(args['timesleep'])
		counter = 0


# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
