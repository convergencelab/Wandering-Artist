/*
 * Noah Barrett
 * 2020-08-27
 * Behaviour for Wandering Artist V1.1:
 * The initial autonomous behaviour of the wandering artist is very simple:
 *    1) Drive until a obstruction is detected
 *    2) Once obstruction is detectected, back up until enough space is established between robot and obstruction
 *    3) perform 180 degree turn, so that the ultrasound sensor can detect obstructions behind it and camera is facing detected obstruction
 *    4) While there is no obstruction behind robot and object is not detected in front: continue backing up and periodically sampling images
 *    5) after threshold is complete, randomly perturb and continue autonomously sampling environment
 * Benefits of implementation:
 *    - Will get job done
 *    - Incorporates some basic model of environment
 * Drawbacks of implementation:
 *    - will take excessive amounts of images
 *    - very over simplified, hardware does not allow for precise measurements
 *    
 *Big Problem:
 *  How do we keep track of all the distance covered? 
 *  
 *  NOTE: Front of WA = Camera facing side
 *        Back = Ultrasound side
 *        
 *        Positive rotation = right(+), left(-)
 *        Negative rotation = right(-), left(+)
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
/*
 * every time WA turns it must add it to turn time ref
 * once it writes the turn time and travel time to python
 * we must rest both times. 
 */

/*MEASUREMENTS FOR SERIAL COMM*/
//rather than a single value, make an dynamic array that stores all of
//the actions until a image should be taken 
// to ensure simplicity for serial communication: use a single array
//every addition will have 3 values and so it must be asserted that the 
//array's size is a factor of 3
// allow for 3 instances of a change off the bat, if more we will grow array
int MaxArrSize = 12;                    //allow for growth of array
int CurArrSize = 0;                     //current size of array, also used as index

//float *Location_Ref = new float[MaxArrSize];
float *Location_Ref = (float*)malloc(sizeof(float) * MaxArrSize);

float TurnTimeRef = 0.0;                //used to keep reference of every turn
float TravelTimeRef = 0.0;              //used to keep reference of travel
float UltraSoundRef = 0.0;              // used to keep reference of ultrasound distance 
float Forwards;                         // bool for either backwards or forwards
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

  Serial.begin(9600); // use the same baud-rate as the python side
}

/*******************************************************************************/
/*
 drive autonomously until finding an obstruction, take series of images while 
 backing up 
  -for each image take snapshot and continue backing up 
  -
  ** Two forms of measuring distance: 1 - time traveled, distance from sensor
 */
 // so when backing up and not travelling for a specific amount of time
 // we will use the ultrasound sensor to measure the distance travelled. 

void loop()
{
  //DETECT THE DISTANCE READ BY THE DISTANCE SENSOR
  distance = getDistance();

  if (digitalRead(switchPin) == LOW) { //if the on switch is flipped
    /*SCENARIO 1: OBSTRUCTION*/
    if (distance < 10) {              //if an obstruction is detected
      /*first if we have already been travelling for awhile, we need to log travel time forward*/
      if (TravelTimeRef != 0.0){
        logLocationRef();
      }
      //stop for 2s
      rightMotor(0);
      leftMotor(0);
      delay(200);
      //back up and turn
      //stop for a moment
      //back up: we need about 10 inches to do 180
      // WRT camera, this is actually forwards so we are not technically backing up
      Forwards = 1.0;
      while (distance < 10){
        rightMotor(-255);
        leftMotor(-255);
        //measure distance using ultrasound sensor
        // measure going to be difference between old and new distance
        // += distance moved forward wrt camera
        UltraSoundRef -= distance;
        distance = getDistance();
        UltraSoundRef += distance;
      }
      //STOP
      rightMotor(0);
      leftMotor(0);
      delay(200);
      
      //one eighty: 
      rightMotor(255);
      leftMotor(-255);
      delay(oneEightyTime);
      
      // record time
      TurnTimeRef += oneEightyTime;
      
      //stop
      rightMotor(0);
      leftMotor(0);
      delay(200);
      
      /*COMMUNICATE WITH PYTHON*/
      // take initial image
      logLocationRef();
      sendLocationRef();
      
     //slowly back up until rear detects object (backup = forward as system will be in opposite direction) 
      // backwards WRT camera
      Forwards = 0.0;
      while (distance > 10){
        rightMotor(255);
        leftMotor(255);
        delay(200);
        TravelTimeRef += 200;
        //stop
        rightMotor(0);
        leftMotor(0);
        delay(200);
        
        /*COMMUNICATE WITH PYTHON*/
        // one of the sequence of images taken while backing up
        logLocationRef();
        sendLocationRef();
        
        distance = getDistance();
      }
      
      // randomize direction
      randomPerturb();
      //log random perturb
      logLocationRef();
      distance = getDistance();
      
      /*SCENARIO 2: NO OBSTRUCTION*/
      } else {
        Forwards = 0.0;
        /*COMMUNICATE WITH PYTHON*/                     
        //move forward (back wards WRT Camera)
        rightMotor(255);
        leftMotor(255);
        delay(200);
        // no need to log as we will just add it to total, no distance change
        TravelTimeRef += 200;
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
        // measure going to be difference between old and new distance
        UltraSoundRef -= distance;
        distance = getDistance();
        UltraSoundRef += distance;
      }
  // randomly turn left or right
  //CW = -
  if(rand()%2){
    rightMotor(-255);
    leftMotor(255);
    TurnTimeRef-=randomTurnTime;
  }
  //CCW = +
  else{
    rightMotor(255);
    leftMotor(-255);
    TurnTimeRef+=randomTurnTime;
  }
  delay(randomTurnTime);
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
/********************************************************************************/
void logLocationRef(){
  /*
   * loads all current values into array
   * resets all vals
   * location ref stores values in order:
   * TurnTimeRef
   * TravelTimeRef
   * UltraSoundRef
   * Forwards
   */

  //before adding new val must ensure that arr is big enough
  CheckArr();
  //TurnTimeRef
  Location_Ref[CurArrSize] = TurnTimeRef;
  CurArrSize++;
  
  //TravelTimeRef
  Location_Ref[CurArrSize] = TravelTimeRef;
  CurArrSize++;
  
  //UltraSoundRef
  Location_Ref[CurArrSize] = UltraSoundRef;
  CurArrSize++;
  
  //Forwards
  Location_Ref[CurArrSize] = Forwards;
  CurArrSize++;

  //reset all references
  TurnTimeRef = 0.0;
  TravelTimeRef = 0.0;
  UltraSoundRef = 0.0;
}
// reallocate mem for array
void CheckArr(){
  if (CurArrSize > MaxArrSize){
    MaxArrSize*=2;
    Location_Ref = (float*)realloc(Location_Ref, sizeof(float) * MaxArrSize);
  }
}



// send array via serial
void sendLocationRef(){
  //send array, this will indicate that photo should be taken
  
  for(int i = 0; i < CurArrSize; i++){
    Serial.println((int)Location_Ref[i]);
  }
  // reset array 
  CurArrSize = 0;

  // wait for python to confirm photo taken
  while (Serial.available() == 0) {
      delay(50);
  }
}
