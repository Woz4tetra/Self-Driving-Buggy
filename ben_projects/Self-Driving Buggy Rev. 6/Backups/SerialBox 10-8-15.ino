
/**
*  @file SerialBox.ino
*  
*  Self Driving Buggy sensor board drivers and serial communication
*  
*  @author Ben Warwick
*  @author Nat Jeffries
*  Add yourselves to authors field upon contribution!
*  
*  In order to run this code you need the following libraries:
*  https://github.com/ivanseidel/DueTimer
*  MPU6050 drivers (built-in ?)
*  Wire.h libary (built-in)
*  
*/

#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"
#include "DueTimer.h"

#include "SerialPacket.h"
#include "defines.h"

#define LED13_PIN 13
#define ENCODER_PIN A0

#define THRESHOLD_HIGH 900
#define THRESHOLD_LOW 800

#define RAD_M 0.279
#define CIR_M (RAD_M*PI)

SerialPacket Packet;

bool fake_led = false;
uint8_t fake_sensor_8bit = 0;
uint16_t fake_sensor_16bit = 0;
uint8_t fake_gps[8];
uint8_t fake_motor = 0;

uint8_t command_id = 0;
uint8_t payload = 0;

//MPU6050 accelgyro;
int pos;
//Servo servo1;
int16_t ax, ay, az;
int16_t gx, gy, gz;

uint8_t accel_array[6];

double total_distance = 0.0;

void setup()
{
    Packet.begin(115200, 2);
    
    pinMode(LED13_PIN, OUTPUT);
    pinMode(A0, INPUT);
//    servo1.attach(2);
    pos = 0;
    
//    Wire.begin();
//    accelgyro.initialize();
    
    handshake();
}

void loop()
{
    delay(3);
}

/*
    SerialEvent occurs whenever a new data comes in the
    hardware serial RX.  This routine is run between each
    time loop() runs, so using delay inside loop can delay
    response.  Multiple bytes of data may be available.
*/

void serialEvent()
{
    int result = Packet.readSerialData();
    if (result == 1)
    {
        command_id = Packet.getCommandID();
        payload = Packet.getPayload();
        
        while (Serial.read() > 0) {  }
        Serial.flush();
    }
    else if (result == 2)
    {
        if (command_id == FAKE_LED)
        {
            fake_led = (bool)payload;
            Packet.sendCommandReply(command_id, (uint8_t)(fake_led));
        }
        else if (command_id == FAKE_SENSOR_8BIT)
        {
            Packet.sendData8bit(command_id, fake_sensor_8bit);
            
            fake_sensor_8bit = (fake_sensor_8bit + 1) & 0xff;
        }
        else if (command_id == FAKE_SENSOR_16BIT)
        {
            Packet.sendData16bit(command_id, fake_sensor_16bit);
            
            if (fake_sensor_16bit == 0) {
                fake_sensor_16bit = 1;
            }
            else {
                fake_sensor_16bit = (fake_sensor_16bit * 2) & 0xffff;
            }
        }
        else if (command_id == LED_13)
        {
            digitalWrite(LED13_PIN, payload);
            Packet.sendCommandReply(command_id, payload);
        }
        else if (command_id == FAKE_MOTOR)
        {
            fake_motor = payload;
            Packet.sendCommandReply(command_id, fake_motor);
        }
        else if (command_id == ACCEL)
        {
//            accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
            ax = random(-0x8000, 0x8000 - 1);
            ay = random(-0x8000, 0x8000 - 1);
            az = random(-0x8000, 0x8000 - 1);
            
            accel_array[0] = ax >> 8;
            accel_array[1] = ax & 0xffff;
            accel_array[2] = ay >> 8;
            accel_array[3] = ay & 0xffff;
            accel_array[4] = az >> 8;
            accel_array[5] = az & 0xffff;
            
            Packet.sendDataArray(accel_array, 6);
        }
        else if (command_id == ENCODER)
        {
            
        }
    }
}

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}