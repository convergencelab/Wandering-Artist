

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
int switchPin = 7;
int one_eighty_time = 600;
const int distance_threshold = 10;
int distance = 0;


void setup() {
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
  // put your setup code here, to run once:
  Serial.begin(115200); // use the same baud-rate as the python side
}
int count = 0;
void loop() {
  
  rightMotor(255);
  leftMotor(255);
  delay(200);
  // put your main code here, to run repeatedly:
  //DETECT THE DISTANCE READ BY THE DISTANCE SENSOR
  //distance = getDistance();
  // if detects something in sensor, 
  // use object detection 
  // if object detected, make artpiece!
  // else: wander! 
  // need to implement a wandering feature
  //if ( distance < distance_threshold) {
      //stop
   //   rightMotor(0);
   //   leftMotor(0);
      //isObject(true);
      
      
      
  //}
 // else{
    //isObject(false);
   // wander();
   // rightMotor(255);
  //  leftMotor(255);
  //
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
/*
void wander(){
  //make robot autonomously wander incremental amount. 
  
}


bool isObject(bool detection){
  //if distance sensor triggered, check camera to see if it is a object
  //write to python
  Serial.print(1, DEC);
  
  
  while(true){
    if(Serial.available() > 0) {
      // what does it come back as ? string? 
      
      //serial_out = Serial.read();
      // 0 for not object back up
      //if (serial_out == 0) {
      //  distance = getDistance();
        //back up
       // if (distance < distance_threshold){
          //cannot back up any more, therefor not an object. 
        //  return false;
       // }
        //else{
            // back up 
          //  rightMotor(-255);
           // leftMotor(-255);
           // rightMotor(0);
           // leftMotor(0);
            // trigger another object detection attempt
           // Serial.print(1, DEC); 
        //}
      }
      // 1 for object, wander!
      else{
        wander();
      }
      
    }
  }
// }



void turn(){
    rightMotor(255);
    leftMotor(-255);
    delay(one_eighty_time);
}
*/
