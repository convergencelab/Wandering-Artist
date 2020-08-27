"""
Noah Barrett
2020-08-27
Simulating a object detection for arduino
to test physical functionality of system:

Program will take arduino request, delay then respond.

"""

import serial, time
Experiment_title = "Communication Test"

## Connect Arduino ##
arduino = serial.Serial('COM8', 115200, timeout=.1)
flag_descriptions = {
    0:"No Obstruction",
    1:"Obstruction"
}
# TEST 1: detect obj right off the bat
while(True):
    # listen for arduino
    time.sleep(1)
    flag = arduino.readline()[:-2]
    print(flag)
    if flag:
        # right now any flag is considered obj detection
        isPotentialOBJ = int(flag)
        arduino.flush()
        print(flag_descriptions[isPotentialOBJ])
        # write 1: this indicates obj succesfully detected
        # and style transfer performed
        time.sleep(10)
        arduino.write(b"1")

