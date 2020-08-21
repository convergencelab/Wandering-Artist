/*
//initial test for arduino
void setup() {
  Serial.begin(115200); // use the same baud-rate as the python side
}
void loop() {
  Serial.println("Hello world from Ardunio!"); // write a string
  delay(1000);
}
*/
//test connection from python to arduino
void setup() {
  Serial.begin(115200);
}

void loop() {
  if(Serial.available() > 0) {
    char data = Serial.read();
    char str[2];
    str[0] = data;
    str[1] = '\0';
    Serial.print(str);
  }
}
