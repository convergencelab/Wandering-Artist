import serial, time
arduino = serial.Serial('COM8', 115200, timeout=.1)
time.sleep(1) #give the connection a second to settle

while True:
    arduino.write(b"Hello from Python!")
    data = arduino.readline()[:-2] #the last bit gets rid of the new-line chars
    if data:
        print(data)