
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
//TODO: add servo and gps support

#include "I2Cdev.h"
#include "MPU6050.h"
#include "Wire.h"
#include "DueTimer.h"

#include "SerialPacket.h"
#include "defines.h"

/* Command IDs */
#define ACCEL_GYRO 0x00
#define ENCODER 0x01
#define SERVO 0x02
#define GPS 0x03
#define LED13 0x04

/* IMU Globals */
MPU6050 accelgyro;
int pos;
//Servo servo1;
int16_t ax, ay, az;
int16_t gx, gy, gz;

/* Distance encoder Globals */
bool is_in_range; //if true, trigger when we see out-of-range value
int last_rising_edge; //ms
volatile int curr_distance;//inches... subject to group consensus

#define HYST_TRIG_HIGH 950 //TODO: Tune these based on OBSERVED values
#define HYST_TRIG_LOW 850
#define WHEEL_CIR (10.0 * PI)
#define ADC_POLLING_PERIOD_US 1000 //1KHz polling rate
/*
 The following back-of-the-envelope calcultaions indicate max speed:
 Assume we must poll at least 50x per revolution in order to 
 ALWAYS detect the magnet (this is conservative).
 Inches per Revolution = 31.415
 1KHz sample rate => 20 revolutions per second at 50 samples/rev
 628.3 inches per second => (approx) 37mph
 */

/* handler for timer interrupt during which ADC is polled */
void handler()
{
    int hall_value = analogRead(A0);
    
    if (is_in_range && (hall_value > HYST_TRIG_HIGH))
    {
        curr_distance += WHEEL_CIR;
        is_in_range = false;
    }
    else if (!is_in_range && (hall_value <= HYST_TRIG_LOW)) {
        is_in_range = true;
    }
}


void setup()
{
    /*disable interrupts to ensure we won't receive the first timer 
     or I2C interrupt before we are ready*/
    noInterrupts();
    
    pinMode(A0, INPUT);
    //servo1.attach(2);
    
    Packet.begin(115200, 2);
    
    Wire.begin(); //I2C library
    accelgyro.initialize(); //IMU library
    
    is_in_range = false; //make sure we don't start at > 0 distance
    curr_distance = 0;
    
    Timer3.attachInterrupt(handler); //handler is a function pointer
    Timer3.start(ADC_POLLING_PERIOD_US);
    interrupts();
    
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
        if (command_id == ACCEL_GYRO)
        {
            accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
            
            accel_array[0] = ax >> 8;
            accel_array[1] = ax & 0xffff;
            accel_array[2] = ay >> 8;
            accel_array[3] = ay & 0xffff;
            accel_array[4] = az >> 8;
            accel_array[5] = az & 0xffff;
            
            accel_array[6] = gx >> 8;
            accel_array[7] = gx & 0xffff;
            accel_array[8] = gy >> 8;
            accel_array[9] = gy & 0xffff;
            accel_array[10] = gz >> 8;
            accel_array[11] = gz & 0xffff;
            
            Packet.sendDataArray(accel_array, 12);
        }
        else if (command_id == ENCODER) {
            Packet.sendData16bit(command_id, curr_distance);
        }
        else if (command_id == SERVO)
        {
            
        }
        else if (command_id == GPS)
        {
            
        }
        else if (command_id == LED_13)
        {
            digitalWrite(LED13_PIN, payload);
            Packet.sendCommandReply(command_id, payload);
        }
    }
}

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}