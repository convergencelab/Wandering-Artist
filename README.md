# Wandering-Artist
Autonomous Art Generation

Robot will autonomously detect objects and perform style transfers on images
to make interesting interpretations of the world it is taking in

<h2>Section 1: Robot</h2>
The robot will be equiped with a ultrasound sensor to aid in the initial dection of objects. i.e.
if obstruction within x cm, run object detection with camera. If object make artistic interpretation

<h3>Components</h3>
- 2 gear motors
- 1 ultrasonic distance sensor
- 1 switch
- 1 motor driver
- jumper wires
- 1 sparkfun redboard

<h3>Camera used</h3> 
   Iphone camera, feed hosted 
   
![Sample of Camera Feed]("./tests/assets/original.png")

<h2>Section 2: Software</h2>
The Wandering artist will use different deep learning techniques to interpret the world
<h3>object detection</h3> 
if ultrasound detects obstruction: 
    turn 180 degrees and begin backing up until full object in image 
    and sensor behind is safe. 

![Sample of Object Detection]("./tests/assets/detected.png")

<h3>Style Transfer</h3> 
Perform a style transfer on detected object with any arbitrary style. For example below is 
a Van Gogh Starry Night transfer onto my cup of coffee. 
![Comparison]("./tests/assets/style_transfer_comp.png")
![Sample of Style]("./tests/assets/starrynight_style.png")
![Sample of Transfer]("./tests/assets/transferred_style.png")
   
   
