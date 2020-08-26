import serial, time
arduino = serial.Serial('COM8', 115200, timeout=.1)
time.sleep(1) #give the connection a second to settle
c = 0
while True:
    if c%2:
        arduino.write(b"1")
    else:
        arduino.write(b"0")
    c+=1
    data = arduino.readline() #the last bit gets rid of the new-line chars
    if data:
        print(data)
    #else:
       # print("nope")
    #    print(int(data))