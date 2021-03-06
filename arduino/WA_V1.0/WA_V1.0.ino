/*
 * Noah Barrett
 * 2020-08-27
 * Behaviour for Wandering Artist V1:
 * The initial autonomous behaviour of the wandering artist is very simple:
 *    1) Drive until a obstruction is detected
 *    2) Once obstruction is detectected, back up until enough space is established between robot and obstruction
 *    3) perform 180 degree turn, so that the ultrasound sensor can detect obstructions behind it and camera is facing detected obstruction
 *    4) While there is no obstruction behind robot and object is not detected in front: continue backing up and periodically sampling for objects
 *    5) If object is detected: wait until style transfer is complete, else: not an object, no style transfer performed
 *    6) Randomly change direction to continue wandering
 * Benefits of implementation:
 *    - Simple to understand
 *    - Will get basic job done
 * Drawbacks of implementation:
 *    - This behaviour is extremely simple and so it likely will not be overly succesful. 
 *    - Does not handle edge cases of getting stuck, should implement some sort of method of detecting if a robot is stuck
 *    - Turning is based on time, this is a very innaccurate method of consistently turning robot
 *    - May not properly handle delay times between Deep Learning Computations and robot
 */


/*PINS*/
//the right motor will be controlled by the motor A pins on the motor driver
const int AIN1 = 13;           //control pin 1 on the motor driver for the right motor
const int AIN2 = 12;            //control pin 2 on the motor driver for the right motor
const int PWMA = 11;            //speed control pin on the motor driver for the right motor

//the left motor will be controlled by the motor B pins on the motor driver
const int PWMB = 10;           //speed control pin on the motor driver for the left motor
const int BIN2 = 9;           //control pin 2 on the motor driver for the left motor
const int BIN1 = 8;           //control pin 1 on the motor driver for the left motor

//distance variables
const int trigPin = 6;
const int echoPin = 5;

int switchPin = 7;             //switch to turn the robot on and off

float distance = 0;            //variable to store the distance measured by the distance sensor
float l_distance = 0;
float r_distance = 0;

//robot behaviour variables
int backupTime = 300;           //amount of time that the robot will back up when it senses an object
int turnTime = 200;             //amount that the robot will turn once it has backed up
int oneEightyTime = 1800;       //yikes

/********************************************************************************/
void setup()
{
  pinMode(trigPin, OUTPUT);       //this pin will send ultrasonic pulses out from the distance sensor
  pinMode(echoPin, INPUT);        //this pin will sense when the pulses reflect back to the distance sensor

  pinMode(switchPin, INPUT_PULLUP);   //set this as a pullup to sense whether the switch is flipped


  //set the motor control pins as outputs
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);

  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  Serial.begin(115200); // use the same baud-rate as the python side
}

/*******************************************************************************/
/*
 drive autonomously until finding an object, back up until object is in good sight,
 snap picture, do style transfer carry on and continue autonomously driving
 */
void loop()
{
  //DETECT THE DISTANCE READ BY THE DISTANCE SENSOR
  distance = getDistance();

  if (digitalRead(switchPin) == LOW) { //if the on switch is flipped
    /*SCENARIO 1: OBSTRUCTION*/
    if (distance < 10) {              //if an object is detected
      //back up and turn
      //stop for a moment
      rightMotor(0);
      leftMotor(0);
      delay(200);
      //back up: we need about 10 inches to do 180
      while (distance < 10){
        rightMotor(-255);
        leftMotor(-255);
        distance = getDistance();
      }
      //STOP
      rightMotor(0);
      leftMotor(0);
      delay(200);
      
      //one eighty
      rightMotor(-255);
      leftMotor(255);
      delay(oneEightyTime);

      //stop
      rightMotor(0);
      leftMotor(0);
      delay(200);
      /*COMMUNICATE WITH PYTHON*/
      //11 == obstruction
      Serial.println("011");
      
     //slowly back up until rear detects object (backup = forward as system will be in opposite direction) 
      while (distance > 10){
        rightMotor(255);
        leftMotor(255);
        delay(200);
        //stop
        rightMotor(0);
        leftMotor(0);
        delay(200);
        // wait for python 
        while (Serial.available() == 0) {
            delay(50);
        }
        char data = Serial.read();
        if(data == "001"){
          //succesfully detected and performed style transfer
          //exit loop
          break;
        }
        distance = getDistance();
      }
      if (distance < 10){
        Serial.println("011");
      }
      Serial.println("100");
      // randomize direction
      randomPerturb();
      distance = getDistance();
      
      /*SCENARIO 2: NO OBSTRUCTION*/
      } else {
        /*COMMUNICATE WITH PYTHON*/
        //10 == no obstruction
        Serial.println("010");                       
        //move forward
        rightMotor(255);
        leftMotor(255);
        delay(200);
        
      }
  }
  else { 
    //if the switch is off then stop
    rightMotor(0);
    leftMotor(0);
    delay(50);
  }
}

/********************************************************************************/
void rightMotor(int motorSpeed)                       //function for driving the right motor
{
  if (motorSpeed > 0)                                 //if the motor should drive forward (positive speed)
  {
    digitalWrite(AIN1, HIGH);                         //set pin 1 to high
    digitalWrite(AIN2, LOW);                          //set pin 2 to low
  }
  else if (motorSpeed < 0)                            //if the motor should drive backward (negative speed)
  {
    digitalWrite(AIN1, LOW);                          //set pin 1 to low
    digitalWrite(AIN2, HIGH);                         //set pin 2 to high
  }
  else                                                //if the motor should stop
  {
    digitalWrite(AIN1, LOW);                          //set pin 1 to low
    digitalWrite(AIN2, LOW);                          //set pin 2 to low
  }
  analogWrite(PWMA, abs(motorSpeed));                 //now that the motor direction is set, drive it at the entered speed
}

/********************************************************************************/
void leftMotor(int motorSpeed)                        //function for driving the left motor
{
  if (motorSpeed > 0)                                 //if the motor should drive forward (positive speed)
  {
    digitalWrite(BIN1, LOW);                         //set pin 1 to high
    digitalWrite(BIN2, HIGH);                          //set pin 2 to low
  }
  else if (motorSpeed < 0)                            //if the motor should drive backward (negative speed)
  {
    digitalWrite(BIN1, HIGH);                          //set pin 1 to low
    digitalWrite(BIN2, LOW);                         //set pin 2 to high
  }
  else                                                //if the motor should stop
  {
    digitalWrite(BIN1, LOW);                          //set pin 1 to low
    digitalWrite(BIN2, LOW);                          //set pin 2 to low
  }
  analogWrite(PWMB, abs(motorSpeed));                 //now that the motor direction is set, drive it at the entered speed
}

/********************************************************************************/
void randomPerturb()
{ 
  //random amount of time to turn between 200 and 1000 ms
  float randomTurnTime;
  randomTurnTime = (rand() % 800) + 200; 
  
  distance = getDistance();
  while (distance < 10){
        rightMotor(-255);
        leftMotor(-255);
        distance = getDistance();
      }
  // randomly turn left or right
  if(rand()%2){
    rightMotor(-255);
    leftMotor(255);
  }
  else{
    rightMotor(255);
    leftMotor(-255);
  }
  delay(randomTurnTime);
  //stop for 50ms
  //rightMotor(0);
  //leftMotor(0);
  //delay(50);
  
}
/********************************************************************************/
//RETURNS THE DISTANCE MEASURED BY THE HC-SR04 DISTANCE SENSOR
float getDistance()
{
  float echoTime;                   //variable to store the time it takes for a ping to bounce off an object
  float calculatedDistance;         //variable to store the distance calculated from the echo time

  //send out an ultrasonic pulse that's 10ms long
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  echoTime = pulseIn(echoPin, HIGH);      //use the pulsein command to see how long it takes for the
                                          //pulse to bounce back to the sensor

  calculatedDistance = echoTime / 148.0;  //calculate the distance of the object that reflected the pulse (half the bounce time multiplied by the speed of sound)

  return calculatedDistance;              //send back the distance that was calculated
}
