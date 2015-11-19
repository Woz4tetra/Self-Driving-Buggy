
#include <MPU9250.h>
#include <HallEncoder.h>
#include <MyGPS.h>
#include <SerialParser.h>

#include <Sensor.h>
#include <Command.h>

const int baud = 115200;
const int node = 2;

char object_id = 0;
unsigned int* payload = new unsigned int;

char accelgyro_buffer[14];
char magnet_buffer[7];

void imu_update(char* data, void* new_data, const int size)
{
    for (int index = 0; index < size; index++) {
        data[index] = ((unsigned char*)new_data)[index];
    }
}
void encoder_update(char* data, void* new_data, const int size)
{
    unsigned long deref_data = *(unsigned long*)new_data;
    
    // size == 4 (8 hex characters)
    for (int index = 0; index < size; index++)
    {
        data[index] = (unsigned char)(deref_data & 0xff);
        deref_data = deref_data >> 8;
    }
}




void to_hex(float input, char *array, int start)
{
    byte* bytearray = (byte*) &input;
    short float_length = 4;
    start *= float_length;
    
    for (int index = float_length - 1; index >= 0; index--) {
        array[((float_length - 1) - index) + start] = bytearray[index];
    }
}
void gps_update(char* data, void* new_data, const int size)
{
    gps_data deref_data = (gps_data)(new_data);
    float* float_array = deref_data->data;
    
    for (int float_index = 0; float_index < (size - 2) / 4; float_index++) {
        to_hex(float_array[float_index], data, float_index);
    }
    data[16] = (deref_data->quality)[0];
    data[17] = (deref_data->quality)[1];
}

sensor_t accel, gyro, magnet, encoder, gps;

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

void setup()
{
    begin_serial(baud);
    
    char sensor_ids[5] = {'a', 'b', 'c', 'd', 'e'};//{0, 1, 2, 3, 4};
    
    accel = sensor_new(node, sensor_ids[0], 6, &imu_update);
    gyro = sensor_new(node, sensor_ids[1], 6, &imu_update);
    magnet = sensor_new(node, sensor_ids[2], 6, &imu_update);
    
    encoder = sensor_new(node, sensor_ids[3], 4, &encoder_update);
    gps = sensor_new(node, sensor_ids[4], 18, &gps_update);
    
//    encoder_setup();
//    gps_setup();
//    mpu_setup();
    
//    handshake();
    Serial.println("Ready!");
}

void loop()
{
//    mpu_update(accelgyro_buffer, magnet_buffer);
    object_id = read_serial(payload);
//    Serial.println("thing 6");
    
//    accelgyro_buffer[0] = random(0, 0xff);
//    accelgyro_buffer[1] = random(0, 0xff);
//    accelgyro_buffer[2] = random(0, 0xff);
//    accelgyro_buffer[3] = random(0, 0xff);
//    accelgyro_buffer[4] = random(0, 0xff);
//    accelgyro_buffer[5] = random(0, 0xff);
    
//    if (object_id == '\0') {
//        return;
//    }
    
//    if (sensor_ids_equal(accel, object_id))
//    {
//        Serial.println("Received: ");
//        Serial.print(object_id);
//        sensor_update(accel, accelgyro_buffer);
//        sensor_toserial(accel);
//    }
//    
//    else if (sensor_ids_equal(gyro, object_id))
//    {
////        for (int index = 0; index < 6; index++) {
////            accelgyro_buffer[index] = accelgyro_buffer[index + 7];
////        }
//        sensor_update(gyro, accelgyro_buffer);
//        sensor_toserial(gyro);
//    }
//    
//    else if (sensor_ids_equal(magnet, object_id))
//    {
////        sensor_update(magnet, magnet_buffer);
//        sensor_update(magnet, accelgyro_buffer);
//        sensor_toserial(magnet);
//    }
//    
//    else if (sensor_ids_equal(encoder, object_id))
//    {
//        unsigned long* fake_distance = new unsigned long;
//        *fake_distance = random(0, 0xffffffff);
//        sensor_update(encoder, (void*)(encoder_distance()));
//        sensor_toserial(encoder);
//    }
    
//    else if (sensor_ids_equal(gps, object_id))
//    {
//        sensor_update(gps, (void*)(get_gps()));
//        sensor_toserial(gps);
//    }
}


