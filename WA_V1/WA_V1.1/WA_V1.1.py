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
import numpy as np
from Model_Repr import Model_Repr, OUTPUT_DIR

### Model Representation ###
# store all frames in a euclidean representation
Model_Repr = Model_Repr()

## Video Stream ##
EXPERIMENT_TITLE = "WA_V1"
# intialize connection with video stream
url = 'http://192.168.2.122:8080/video'
cap = cv2.VideoCapture(url)

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
arduino = serial.Serial('COM8', 115200, timeout=.1)
arduino_comm = {
                "Photo_Captured":b"0"
}
while(True):
    ret, frame = cap.read()
    # listen for arduino
    time.sleep(1)
    # we will recieve the time spent travelling and the time spent turning from arduino
    comm_string = arduino.readline()

    """
    read data from arduino
    
    store data in Model representation
    """
    #if data:
    """
    take image and store in model
        """
   # else:
    """do not store anything in model"""

    arduino.flush()

    # if not suspecting object show frame
    if frame is not None:
        #if isPotentialOBJ:
        if comm_string:
            # parse comm string
            turn_time = comm_string[0:1]
            travel_time = comm_string[1:2]

            img_title = OUTPUT_DIR + "imgs/" + str(time.localtime())
            cv2.imwrite(img_title, frame)
            Model_Repr.log_new_point(turn_time, travel_time, img_title)
            arduino.write(arduino_comm["Photo_Captured"])

        # cv2.imshow('frame', frame)
        # video.write(frame)

        q = cv2.waitKey(1)
        if q == ord("q"):
            break

# video.release()
cv2.destroyAllWindows()



