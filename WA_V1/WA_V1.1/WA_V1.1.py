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
import serial, time
import datetime
import numpy as np
from Model_Repr import Model_Repr, OUTPUT_DIR
from obj_detection import Object_Detection
from style_transfer import Style_Transfer

### Model Representation ###
# store all frames in a euclidean representation
Model_Repr = Model_Repr()
MAX_IMAGE = 100
OBJ_ACCEPTANCE_THRESHOLD = 0.40

### handling image storage ###

if os.listdir(OUTPUT_DIR):
    m_val = max([int(dir) for dir in os.listdir(OUTPUT_DIR)]) + 1
    IMG_DIR = OUTPUT_DIR + "{}/imgs/".format(m_val)
    MODEL_DIR = OUTPUT_DIR + "{}/model/".format(m_val)
else:
    os.mkdir(OUTPUT_DIR + "1/")
    IMG_DIR = OUTPUT_DIR + "1/imgs/"
    MODEL_DIR = OUTPUT_DIR + "1/model/"
os.mkdir(IMG_DIR)
# child dirs inside new img directory #
RAW_DIR = IMG_DIR + "raw_data/"
os.mkdir(RAW_DIR)
# analyzed data #
IMG_DIR += "Analyzed/"
os.mkdir(IMG_DIR)
# make style and obj dirs #
OBJ_DIR = IMG_DIR + "obj_detection/"
os.mkdir(OBJ_DIR)
STYLE_DIR = IMG_DIR + "style_transfer/"
os.mkdir(STYLE_DIR)


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
            location_ref = [int(val) for val in location_ref]
            #cv2.imshow('frame', frame)
            # save frame
            print(location_ref)


            img_title = RAW_DIR +str(datetime.datetime.now())[:-7].replace(" ", "_").replace(":", "-") +  ".png"
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
        if len(os.listdir(RAW_DIR)) == MAX_IMAGE:
            break
        q = cv2.waitKey(1)
        if q == ord("q"):
            break

# video.release()
cv2.destroyAllWindows()

##################
# Image Analysis #
##################

# Obj detection & Style transfer #
model = Model_Repr._points_on_plane
for point in model.keys():
    img = cv2.imread(model[point])
    det_obj_img, _, classes, scores = Object_Detection(img)

    # get max score
    index = np.argmax(scores)

    # for later use we can include the max classes using classes
    # TODO: incorporate classes for NLP!

    # if score is greater than or equal to our threshold for obj acceptance
    if scores[index] >= OBJ_ACCEPTANCE_THRESHOLD:
        # perform style transfer on image
        style_dir = STYLE_DIR + os.path.basename(model[point])
        # perform style transfer
        styled_img = Style_Transfer(model[point])
        # write styled img
        cv2.imwrite(style_dir, styled_img)

        obj_dir = OBJ_DIR + os.path.basename(model[point])
        # write obj detection img
        cv2.imwrite(obj_dir, det_obj_img)

        # save images as tuple pair in model rep
        model[point] = obj_dir, style_dir

    else:
        # remove point from the model representation
        Model_Repr.remove_point(point)

##############
# SAVE MODEL #
##############
model_dir = MODEL_DIR + "model_" + m_val +".json"
Model_Repr.save_model(model_dir)


