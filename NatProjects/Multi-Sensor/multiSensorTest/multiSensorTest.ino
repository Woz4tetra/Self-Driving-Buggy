#include <Servo.h>

/** @file multiSensorTest.ino
 *  
 *  @author Nat Jeffries
 */

#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"

MPU6050 accelgyro;
int pos;
Servo servo1;
int16_t ax, ay, az;
int16_t gx, gy, gz;

void setup() {
  // put your setup code here, to run once:
  pinMode(A0, INPUT);
  servo1.attach(2);
  pos = 0;
  Serial.begin(9600);
  Wire.begin();
  accelgyro.initialize();
}

int dir = 1;

void loop() {
  // put your main code here, to run repeatedly:
  accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  Serial.print("ax: "); Serial.print(ax/160);
  Serial.print("ay: "); Serial.print(ay/160);
  Serial.print("az: "); Serial.println(az/160);
  //Serial.println(analogRead(A0));
  delay(100);
  pos += dir;
  if (pos >= 170) dir = -1;
  if (pos == 0) dir = 1;
  servo1.write(pos);
}
