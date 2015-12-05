
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


#define DEBUG

Servo steering_servo;
uint8_t accelgyro_buf[14];
uint8_t magnet_buf[7];
uint64_t hall_distance = 0;
uint8_t gps_array[gps_array_len];
#define LED13_PIN 13


// sensor id (2), tab (1), data length (2), tab(1), data (1...16), newline (1)
const uint8_t packet_size = 23;
char packet[packet_size]; 

uint8_t data_len = 0;
uint8_t command_id = 0;
uint64_t payload = 0;

bool new_command_found = false;

char incomming = 0;
uint8_t current_index = 0;

uint8_t current_sensor = 0;
uint8_t num_sensors = 3;

void setup()
{
    Serial.begin(115200);
//    mpu_setup();
//    Serial.println("MPU initialized!");
    
    gps_setup();
    Serial.println("GPS initialized!");
    
    encoder_setup();
    Serial.println("Encoder initialized!");
    
    pinMode(LED13_PIN, OUTPUT);
    Serial.println("LED13 initialized!");
    
    steering_servo.attach(3);
    steering_servo.write(0);
    
    Serial.println("Servo initialized!");
    
    for (size_t index = 0; index < packet_size; index++) {
        packet[index] = 0;
    }
    
    handshake();
}

void loop()
{
    update_packet();
    
    if (new_command_found)
    {
        if (command_id == STEERSERVO_ID) {
            steering_servo.write(payload & 0xff);
        }
        else if (command_id == LED13_ID) {
            digitalWrite(LED13_PIN, payload & 0xff);
        }
        
        new_command_found = false;
    }
    

    hex_print(current_sensor);
    Serial.write('\t');
    
/*  
    if (current_sensor == IMU_ID)
    {
        mpu_update(accelgyro_buf, magnet_buf);
        
        for (int index = 0; index < 14; index++) {
            hex_print(accelgyro_buf[index]);
        }
        for (int index = 0; index < 7; index++) {
            hex_print(magnet_buf[index]);
        }
    }*/
    if (current_sensor == GPS_ID)
    {
        gps_update(gps_array);
        
        for (int index = 0; index < gps_array_len; index++) {
            hex_print(gps_array[index]);
        }
    }
    else if (current_sensor == ENCODER_ID)
    {
        hall_distance += 1;
//        hall_distance = encoder_distance();
        for (int digit = 0; digit < 8; digit++) {
            hex_print((hall_distance >> (8 * (8 - digit))) & 0xff);
        }
    }
    else
    {
        hex_print(0xff);
    }
    Serial.write('\n');
    
    current_sensor = (current_sensor + 1) % num_sensors;
}


void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {    }
    
    Serial.flush();
}

void hex_print(uint8_t data)
{
    if (data < 0x10) {
        Serial.print("0");
    }
    Serial.print(data, HEX);
}

uint8_t hex_to_dec(char hex_char)
{
    if ('0' <= hex_char && hex_char <= '9') {
        return (uint8_t)(hex_char - '0');
    }
    else if ('a' <= hex_char && hex_char <= 'f') {
        return (uint8_t)(hex_char - 'a') + 10;
    }
    else if ('A' <= hex_char && hex_char <= 'F') {
        return (uint8_t)(hex_char - 'A') + 10;
    }
    else {
        return 0;
    }
}

void update_packet()
{
    while (Serial.available() && incomming != '\n')
    {
        incomming = (char)Serial.read();
        packet[current_index] = incomming;
        current_index += 1;
    }
    
    if (packet[2] == '\t' && packet[5] == '\t' &&
        packet[current_index - 1] == '\n')
    {
        command_id = hex_to_dec(packet[0]) << 4 | hex_to_dec(packet[1]);
        data_len = hex_to_dec(packet[3]) << 4 | hex_to_dec(packet[4]);
        payload = 0;
        
        for (uint8_t index = 0; index < data_len; index++) {
            payload |= hex_to_dec(packet[index + 6]) << (4 * (data_len - index - 1));
        }
//        Serial.print((unsigned long)payload);
        new_command_found = true;
    }
    
    if (incomming == '\n')
    {
//        for (size_t index = 0; index < 7; index++) {
//            Serial.print(" ["); Serial.print(packet[index]); Serial.print("] ");
//        }
//        Serial.print(packet[2]); Serial.print(',');
//        Serial.print(packet[5]); Serial.print(',');
//        Serial.print(packet[current_index - 1], HEX);
//        Serial.println();
        
        incomming = 0;
        current_index = 0;
    }
}



