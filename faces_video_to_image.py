# USAGE
# python recognize_faces_video.py --encodings encodings.pickle
# python recognize_faces_video.py --encodings encodings.pickle --output output/jurassic_park_trailer_output.avi --display 0

# import the necessary packages
from imutils.video import VideoStream
import basic_speech as speech
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os
from PIL import Image
import speech_recognition as sr
from pyHS100 import SmartPlug
from prepare_pictures import prepare_picture,showPIL

plug = SmartPlug("10.254.51.142")
# obtain audio from the microphone

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
ap.add_argument("-y", "--display", type=int, default=1,
	help="whether or not to display output frame to screen")
ap.add_argument("-d", "--detection-method", type=str, default="hog",
	help="face detection model to use: either `hog` or `cnn`")
ap.add_argument("-w", "--width", type=int, default=1500,
	help="width image")

ap.add_argument("-nc", "--ncounts", type=int, default=4,
	help="number of counts before triggering speech")

ap.add_argument("-tout", "--timeout", type=int, default=3,
	help="time before the recording stops in seconds")
ap.add_argument("-ts", "--tsleep", type=int, default=10,
	help="time before starting new conversion again")

args = vars(ap.parse_args())

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())

# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()

counter_frames = 0
# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()

	# convert the input frame from BGR to RGB then resize it to have
	# a width of 1000px (to speedup processing)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	rgb = imutils.resize(frame, width=args['width'])

	#Ratio between original size and resized image
	r = frame.shape[1] / float(rgb.shape[1])

	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
	boxes = face_recognition.face_locations(rgb,
		model=args["detection_method"])
	encodings = face_recognition.face_encodings(rgb, boxes)

	if len(boxes)>0:
		print('face detected')
		counter_frames += 1

	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
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

		# update the list of names
		names.append(name)



	###### The image is given by the variable "frame", and "names" is the list of all the people recognized in the picture. #########
	## if we detect a face more than args['ncounts'] times, we initiate conversation
	if counter_frames == args['ncounts']:
		still_speaking = True
		counter_dialog = 0
		counter_noise = 0
		while still_speaking:
	    # recognizer only records text when loud enough (stop when it hears silence)
			r = sr.Recognizer()
			with sr.Microphone() as source:
				r.adjust_for_ambient_noise(source)
				if counter_dialog == 0:
					if names[0] != 'Unknown':
						image = prepare_picture(frame,boxes,names)
						cv2.imwrite('image.jpg',image)
						img = Image.open('image.jpg')
						img.show()
            #to use our TTS:
            #speech.main(names)
						print("Hello {}!".format(names[0]))

					else:
						print("Hello! Are you here to see anyone?")
						plug.state = "ON"
						time.sleep(5)
						plug.state = "OFF"

				try:

					audio = r.listen(source,timeout=args['timeout'])

					try:

						print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
						print('anything else?')
						counter_dialog += 1
						counter_noise = 0
					except sr.UnknownValueError:
						print("Google Speech Recognition could not understand audio")
						print("Can you repeat that?")
						counter_dialog += 1
						counter_noise +=1
						if counter_noise == 4:
							print('Shutting down, bye for now')
							still_speaking = False
					except sr.RequestError as e:
					    print("Could not request results from Google Speech Recognition service; {0}".format(e))

				except:
				# when silence for more than timeout, raise error and conversation is over

					still_speaking = False




		counter_frames = 0
		time.sleep(args['tsleep'])


	# 	cv2.imshow("Image", frame)
  #   speech.main(names)
	# 	cv2.waitKey(args['time_image']*1000)
	#
	# #### If args['time_image'] = 0, the image is shown indefinitely, until the user presses "q". That can be replaced by any condition.
	# key = cv2.waitKey(1) & 0xFF
	# if key == ord("q"):
	#  		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
