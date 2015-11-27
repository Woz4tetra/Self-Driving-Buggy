
#include <Wire.h>
#include <DueTimer.h>
#include <Adafruit_GPS.h>
#include <HallEncoder.h>
#include <MPU9250.h>
#include <Servo.h>
#include <MyGPS.h>
#include <Utilities.h>


#define IMU_ID 0x00
#define GPS_ID 0x01
#define ENCODER_ID 0x02

#define STEERSERVO_ID 0x00
#define LED13_ID 0x01



Servo steering_servo;
uint8_t accelgyro_buf[14];
uint8_t magnet_buf[7];
uint64_t hall_distance = 0;
uint8_t gps_array[gps_array_len];
#define LED13_PIN 13


// sensor id (2), tab (1), data length (2), tab(1), data (1...16), newline (1)
const uint8_t packet_size = 23;

char packet[packet_size]; 
uint8_t command_id = 0;
uint8_t data_len = 0;
uint64_t payload = 0;

bool new_command_found = false;

char incomming = '\0';
uint8_t current_index = 0;

uint8_t current_sensor = 0;


void setup()
{
    mpu_setup();
    
    gps_setup();
    
    encoder_setup();
    
    pinMode(LED13_PIN, OUTPUT);
    
    steering_servo.attach(3);
    steering_servo.write(0);
    
    handshake();
}

void loop()
{
    update_packet();
    
    if (new_command_found)
    {
        if (command_id == STEERSERVO_ID) {
            steering_servo.write((uint8_t)payload);
        }
        else if (command_id == LED13_ID) {
            digitalWrite(LED13_PIN, (uint8_t)payload);
        }
    }
    new_command_found = false;
    
    if (current_sensor == IMU_ID)
    {
        mpu_update(accelgyro_buf, magnet_buf);
        
        hex_print(current_sensor);
        
        for (int index = 0; index < 14; index++) {
            hex_print(accelgyro_buf[index]);
        }
        for (int index = 0; index < 7; index++) {
            hex_print(magnet_buf[index]);
        }
    }
    else if (current_sensor == GPS_ID)
    {
        gps_update(gps_array);
        
        for (int index = 0; index < gps_array_len; index++) {
            hex_print(gps_array[index]);
        }
    }
    else if (current_sensor == ENCODER_ID)
    {
        hall_distance = encoder_distance();
        do
        {
            hex_print(hall_distance & 0xff);
            hall_distance = hall_distance >> 8;
        }
        while (hall_distance > 0);
    }
}


void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

void hex_print(uint8_t data)
{
    if (data < 0x10) {
        Serial.print("0");
    }
    Serial.print(data, HEX);
}


void update_packet()
{
    while (Serial.available() > 0 && incomming != '\n')
    {
        incomming = (char)Serial.read();
        packet[current_index] = incomming;
        current_index += 1;
    }
    if (packet[2] == '\t' && packet[4] == '\t' && packet[current_index - 1] == '\n')
    {
        data_len = (packet[3] << 4) + packet[4];
        
        if ((current_index - 1) - 4 == data_len)
        {
            command_id = (packet[0] << 4) + packet[1];
            
            payload = 0;
            
            for (int index = 0; index < data_len; index++) {
                payload += packet[6 + index] << (4 * (data_len - index));
            }
            incomming = '\0';
            current_index = 0;
        }
        new_command_found = true;
    }
}

