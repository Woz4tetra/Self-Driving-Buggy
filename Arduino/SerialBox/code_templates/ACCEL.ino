/* -------------------- Includes -------------------- */

#include "I2Cdev.h"
#include "MPU9250.h"
#include "Wire.h"

/* -------------------- Globals --------------------- */

MPU9250 accelgyro;

const int data_length = 3;

int16_t accel_int16[data_length];
uint8_t accel_uint8[data_length * 2];

int16_t gyro_int16[data_length];
uint8_t gyro_uint8[data_length * 2];

int16_t magnet_dummy = 0;

void int16_to_uint8(int16_t *int16_array, int int16_length, uint8_t *uint8_array)
{
    for (int index = 0; index < int16_length; index++)
    {
        uint8_array[2 * index + 1] = int16_array[index] & 0xff;
        uint8_array[2 * index] = int16_array[index] >> 8;
    }
}

/* --------------------- Setup ---------------------- */

Wire.begin();

Serial.println("Initializing I2C devices...");
accelgyro.initialize();

Serial.println("Testing device connections...");
Serial.println(accelgyro.testConnection() ? "MPU9250 connection successful" : "MPU9250 connection failed");

delay(1000);

//Mxyz_init_calibrated();

/* ---------------------- Loop ---------------------- */

accelgyro.getMotion9(&accel_int16[0], &accel_int16[1], &accel_int16[2],
                     &gyro_int16[0], &gyro_int16[1], &gyro_int16[2],
                     &magnet_dummy, &magnet_dummy, &magnet_dummy);

/* --------------------- Serial --------------------- */

int16_to_uint8(accel_int16, data_length, accel_uint8);

Packet.sendDataArray(accel_uint8, data_length * 2);
