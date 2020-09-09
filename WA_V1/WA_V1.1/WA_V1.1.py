"""
Wandering Artist V1
Noah Barrett
2020-09-07

This is the first version of the wandering artist, this implementation uses very slow, out of the box
deep learning approaches.

Control Architecture- Reactive: Autonomously drive around until obstruction detected, take series of pictures
                                in hopes of capturing an object to perform style transfer on it.

"""
import os, sys
# object detection parent dir
research_dir = os.path.abspath("../../models/research")
sys.path.append(research_dir)  # To find local version of the library
import cv2
import matplotlib.pyplot as plt
import serial, time
import datetime
import numpy as np
from Model_Repr import Model_Repr, OUTPUT_DIR
from PIL import Image

### Model Representation ###
# store all frames in a euclidean representation
Model_Repr = Model_Repr()
MAX_IMAGE = 100
### handling images ###
IMG_DIR = OUTPUT_DIR+'imgs/'
if not os.path.isdir(IMG_DIR):
    os.mkdir(IMG_DIR)
    IMG_DIR += "/1/"
    os.mkdir(IMG_DIR)
    IMG_DIR += "raw_data/"
    os.mkdir(IMG_DIR)
else:
    m_val = max([int(dir) for dir in os.listdir(IMG_DIR)])+1
    IMG_DIR += "/{}/".format(m_val)
    os.mkdir(IMG_DIR)
    IMG_DIR += "raw_data/".format(m_val)
    os.mkdir(IMG_DIR)

print(IMG_DIR)
## Video Stream ##
EXPERIMENT_TITLE = "WA_V1"
# intialize connection with video stream
url = 'http://192.168.2.122:8080/video'
cap = cv2.VideoCapture(url)
print(OUTPUT_DIR)
# video writer to record outcome
#width, height = (480, 480)
#FPS = 24
# fourcc = cv2.VideoWriter_fourcc(*'MP42')
# video = cv2.VideoWriter('./{}.avi'.format(EXPERIMENT_TITLE), fourcc, float(FPS), (width, height))

## Connect Arduino ##
# V1.0 used flags to determine whether or not there is an obstruction
# lets disregard use of flags for V1.1
# instead arduino will send time spent turning and time spent travelling if obstruction detected
# if no obstruction arduino will not send any information
arduino = serial.Serial('COM8', 9600, timeout=.1)
arduino_comm = {
                "Photo_Captured":b"0"
}
while(True):
    ret, frame = cap.read()
    if frame is not None:
        # listen for arduino
        time.sleep(1)
        # location reference from arduino (bytes)
        location_ref = arduino.readlines()
        print(location_ref)
        if location_ref:
            # convert bytes back to ints
            location_ref = [int.from_bytes(val, byteorder=sys.byteorder, signed=True) for val in location_ref]
            #cv2.imshow('frame', frame)
            # save frame
            print(location_ref)
            s = ''
            for l in location_ref:
                s+=str(l)+"_"

            img_title = IMG_DIR +s[:-1]+  ".png"
            cv2.imshow(img_title, frame)
            cv2.imwrite(img_title, frame)
            #im = Image.fromarray(frame)
            #im.save(img_title)
            # record location
            Model_Repr.log_location_ref(location_ref, img_title)
            arduino.write(arduino_comm["Photo_Captured"])

            # arduino.flush()

        # Model_Repr.plot_model_space()

        # cv2.imshow('frame', frame)
        # video.write(frame)
        if len(os.listdir(IMG_DIR)) == MAX_IMAGE:
            break
        q = cv2.waitKey(1)
        if q == ord("q"):
            break

# video.release()
cv2.destroyAllWindows()



