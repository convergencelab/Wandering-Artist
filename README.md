# Wandering-Artist
Autonomous Art Generation

Robot will autonomously detect objects and perform style transfers on images
to make interesting interpretations of the world it is taking in

<h2>Section 1: Robot</h2>
The robot will be equipped with a ultrasound sensor to aid in the initial detection of objects.

![Sample of Camera Feed](https://github.com/convergencelab/Wandering-Artist/blob/master/tests/assets/WA_V1_.jpg?raw=true)

<h3>Components</h3>
* 2 gear motors
* 1 ultrasonic distance sensor
* 1 switch
* 1 motor driver
* jumper wires
* 1 sparkfun redboard

<h3>Camera used</h3> 
   Iphone camera, feed hosted 
   
![Sample of Camera Feed](https://github.com/convergencelab/Wandering-Artist/blob/master/tests/assets/original.png?raw=true)

<h2>Section 2: Software</h2>
The Wandering artist will use different deep learning techniques to interpret the world
<h3>object detection</h3> 
if ultrasound detects obstruction: 
    turn 180 degrees and begin backing up until full object is detected in image 
    and sensor behind is safe. 

![Sample of Object Detection](https://github.com/convergencelab/Wandering-Artist/blob/master/tests/assets/detected.png?raw=true)

<h3>Style Transfer</h3> 
Perform a style transfer on detected object with any arbitrary style. For example below is 
a Van Gogh Starry Night transfer onto my cup of coffee. 

![Comparison](https://github.com/convergencelab/Wandering-Artist/blob/master/tests/assets/style_transfer_comp.png?raw=true)

<h3>Resulting Image</h3>

![Sample of Transfer](https://github.com/convergencelab/Wandering-Artist/blob/master/tests/assets/transferred_style.png?raw=true)
   
   
<h3>control</h3>
The wandering artist is currently a purely reactive system. This means it does not use any 
deliberative control mechanisms. The behaviour of which it uses is simply:

Does the Ultrasound sensor detect an obstruction?
* yes: back up until there is enough distance to perform a 180 degree rotation,
        perform 180
        back up while continuously taking images of the prospective object, until an obstruction is dettected from behind
        randomly select a new direction to travel in and repeat
* no: continue driving straight 
    
<h3>Model</h3>
The wandering artist models its environment in a relatively crude way due to the lack of sensors 
present in it. The images are stored in a cartesian map, with the origin being the starting place of the 
Wandering Artist. There are a limited amount of states to keep track of in this implemenation of the Wandering Artist. 
The possible states are:
1. Travelling forward (Ultrasound sensor facing potential obstruction, forward)
2. moving backwards to give enough room to perform 180 degree turn
3. Performing a 180 turn to capture potential object
4. travelling away from object (camera facing obstruction, forward)
5. Random permutation 

**Distance travelled**

We must be able to measure how far the robot has travelled backwards and forwards:
* Ultrasound Sensor- When travelling in areas of which an obstruction is detectable, we can utilize the ultrasound 
sensor to measure the distance travelled (units = Inches)
    * used in state **2** to measure distance backed up from obstruction
* Measure time travelled- Using rough estimates, we can determine the amount of distance travelled by using the time 
the motors were rotating and in what direction they were rotating in. (Units = ms) 
    * system travels at a approximate rate of 0.05 Inches/ms
    * used in state **1**, and state **4** to measure the distance travelled based on time of motor activation

`distance = (TravelTimeRef * VELOCITY_I_PER_MS) + UltraSoundRef`

**Trajectory**

With every sequence of travel, the relative position of the system will also depoend on the trajectory
of the system prior to engaging in forward or backwards motion
* Measure Rotation Time - A very crude estimate of trajectory can be by measuring the amount of time the 
system spends rotating. (Units = degrees)
    * system rotates at approximately 10 degrees/ms
    * used in **3** and **5** to determine the amount of rotation performed by the system.
    
With the distance travelled and trajectory, we can determine the systems position relative to its starting point.
This is done using some basic trig, and adding up the trajectories component wise. 

<h3>Image Processing</h3>

The image processing will occur simultaneously with image collection. The system operates in the following way:
* For each image collected, perform object detection
    * if object detected, perform style transfer and store artistic interpretation where original was stored
    * if no object detected, remove image from model
    
**Object Detection**

The current implementation of the wandering artist is using the centernet model, trained on ms-coco dataset. No further 
training is performed. The model is obtained through the tensorflow object detection api, and is not trained on any new 
data. The MS-COCO dataset contains 80 different objects, so this means that the Wandering Artist has a fairly wide range 
of objects to potentially detect (more info at https://cocodataset.org/). 

**Style Transfer**

The style transfer is performed using the Van Gogh Starry Night art piece for all examples shown. The style transfer 
utilizes the first 5 blocks of the VGG-19 Model, trained on the imagenet dataset (www.image-net.org). The first 5 layers of 
this model will contain information about high level relationships, and so prove to be useful in the style transfer operation. 

**Problems with Computation**

The above described Deep Learning image manipulation techniques are realtively computationally heavy and therefore create 
bottlenecks in the systems ability to perform them in real time. Because of this, these tasks are performed separately from
the image collection process. 

    
<h3> Future Improvements</h3>

* More sensors will allow for more accurate internal models of the environment
* The models should be used to influence the systems actions, for example modify the probabilities
associated with the random perturbations, such that it does not head in directions that have already been
explored. 
* Later implementations should include more deep learning models to create different "lifelike" features a
Natural Language Processing Model would be useful in creating realistic captions for the images, or could even 
tell a story with the images. 
* Reinforcement learning could be used in the collection of images, the goal of the system would be to maximize
object detection and centre the object in the frame. 
* Faster deep learning models could promote real time object detections and style transfer. 
* simple image analysis could be used to take properties of images such as dominant colours to further improve 
NLP possibilities. 