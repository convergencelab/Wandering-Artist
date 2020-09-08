# test comm with arduino for WA_V1.1
import serial
arduino = serial.Serial('COM8', 9600, timeout=.1)
while(True):
    # location reference from arduino (bytes)
    location_ref = arduino.readlines()
    if location_ref:
        # convert bytes back to ints
        Location_Ref = [int(val) for val in location_ref]
        print(Location_Ref)
