
#include <MPU9250.h>
#include <HallEncoder.h>
#include <MyGPS.h>
#include <SerialParser.h>
#include <Servo.h>

#include <Sensor.h>
#include <Command.h>

const int baud = 115200;
const int node = 2;

uint8_t object_id = 0;
uint64_t* payload = new uint64_t;

uint8_t accelgyro_buffer[14];
uint8_t magnet_buffer[7];

gps_data* GPS_data;

void imu_update(uint8_t* data, void* new_data, const int size)
{
    for (int index = 0; index < size; index++) {
        data[index] = ((uint8_t*)new_data)[index];
    }
}
void encoder_update(uint8_t* data, void* new_data, const int size)
{
    uint64_t deref_data = *(uint64_t*)new_data;
    
    // size == 4 (8 hex characters)
    for (int index = size - 1; index >= 0; index--)
    {
        data[index] = (uint8_t)(deref_data & 0xff);
        deref_data = deref_data >> 8;
    }
}


void to_hex(float input, uint8_t *array, int start)
{
    byte* bytearray = (byte*) &input;
    short float_length = 4;
    start *= float_length;
    
    for (int index = float_length - 1; index >= 0; index--) {
        array[((float_length - 1) - index) + start] = bytearray[index];
    }
}
void gps_update(uint8_t* data, void* new_data, const int size)
{
    gps_data* deref_data = (gps_data*)(new_data);
    float* float_array = deref_data->data;
    
    for (int float_index = 0; float_index < (size - 2) / 4; float_index++) {
        to_hex(float_array[float_index], data, float_index);
    }
    data[16] = (deref_data->quality)[0];
    data[17] = (deref_data->quality)[1];
}

#define LED13_PIN 13

sensor_t accel, gyro, magnet, encoder, gps;
command_t servo1_command, led13_command;

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

Servo servo1;

void setup()
{
    begin_serial(baud);
    
    accel = sensor_new(node, 1, 6, &imu_update);
    gyro = sensor_new(node, 2, 6, &imu_update);
    magnet = sensor_new(node, 3, 6, &imu_update);
    
    encoder = sensor_new(node, 4, 4, &encoder_update);
    gps = sensor_new(node, 5, 18, &gps_update);
    
    servo1_command = command_new(node, 6);
    led13_command = command_new(node, 7);
    
    encoder_setup();
    gps_setup();
    mpu_setup();
    
    pinMode(LED13_PIN, OUTPUT);
    
    servo1.attach(3);
    servo1.write(0);
    
    *payload = 0;
    GPS_data = gps_data_new();
    
    handshake();
}

void loop()
{
//    mpu_update(accelgyro_buffer, magnet_buffer);
    GPS_data = get_gps();
    object_id = read_serial(payload);
    
    if (sensor_ids_equal(accel, object_id))
    {
        sensor_update(accel, accelgyro_buffer);
        sensor_toserial(accel);
    }
    
    else if (sensor_ids_equal(gyro, object_id))
    {
        for (int index = 0; index < 6; index++) {
            accelgyro_buffer[index] = accelgyro_buffer[index + 7];
        }
        sensor_update(gyro, accelgyro_buffer);
        sensor_toserial(gyro);
    }
    
    else if (sensor_ids_equal(magnet, object_id))
    {
        sensor_update(magnet, magnet_buffer);
        sensor_toserial(magnet);
    }
    
    else if (sensor_ids_equal(encoder, object_id))
    {
        sensor_update(encoder, (void*)(encoder_distance()));
        sensor_toserial(encoder);
    }
    
    else if (sensor_ids_equal(gps, object_id))
    {
        sensor_update(gps, (void*)(GPS_data));
        sensor_toserial(gps);
    }
    
    else if (command_ids_equal(servo1_command, object_id)) {
        servo1.write(*(uint8_t*)payload);
    }
    
    else if (command_ids_equal(led13_command, object_id)) {
        digitalWrite(LED13_PIN, *payload);
    }
}


