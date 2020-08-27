"""
Noah Barrett
2020-08-27
Simulating a object detection for arduino
to test physical functionality of system:

Program will take arduino request, delay then respond.

"""

import serial, time
Experiment_title = "Communication Test"
TEST = 2
## Connect Arduino ##
arduino = serial.Serial('COM8', 115200, timeout=.1)
state_descriptions = {
    b"000":"object not detected",
    b"001":"object detected",
    b"010":"No Obstruction",
    b"011":"Obstruction",
    b"100":"Looking for new object"
}
if TEST == 1:
    # TEST 1: always detect obj
    while(True):
        # listen for arduino
        time.sleep(1)
        state = arduino.readline()[:-2]
        print(state)
        if state:
            # right now any flag is considered obj detection
            isPotentialOBJ = state
            # arduino.flush()
            print(state_descriptions[isPotentialOBJ])
            # write 1: this indicates obj succesfully detected
            # and style transfer performed
            time.sleep(1)
            arduino.write(b"001")

elif TEST == 2:
    # TEST 2: never detect obj
    while(True):
        # listen for arduino
        time.sleep(1)
        state = arduino.readline()[:-2]
        print(state)
        if state:
            # right now any flag is considered obj detection
            isPotentialOBJ = state
            # arduino.flush()
            print(state_descriptions[isPotentialOBJ])
            # write 1: this indicates obj succesfully detected
            # and style transfer performed
            time.sleep(1)
            arduino.write(b"000")