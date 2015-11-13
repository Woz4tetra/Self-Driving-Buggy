
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
 *  Wire.h library (built-in)
 *  /ben_projects/Self-Driving\ Buggy\ Rev.\ 6/board/test_serial.py
 *  
 */

/* ---------------- Includes start ------------------ */
/*                                                    */
#include <SerialPacket.h>
#include "I2Cdev.h"
#include "MPU9250.h"
#include "Wire.h"

/*                                                    */
/* ----------------- Includes end ------------------- */

/* -------------- Command IDs start ----------------- */
/*                                                    */
#define MAGNET_ID 0x00
#define GYRO_ID 0x01
#define ACCEL_ID 0x02
/*                                                    */
/* --------------- Command IDs end ------------------ */

/* -------------- Serial Globals start -------------- */
/*                                                    */
SerialPacket Packet;

const int baud = 38400;
const int node = 2;

int payload = 0;
int command_id = 0;
/*                                                    */
/* --------------- Serial Globals end --------------- */


/* --------------- Auto Globals start --------------- */
/*                                                    */

/* ----- ACCEL globals ----- */
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

/* ----- MAGNET globals ----- */
I2Cdev I2C_M;

const int mag_data_length = 6;

uint8_t magnet_uint8[mag_data_length];
/*                                                    */
/* ---------------- Auto Globals end ---------------- */

/* ================================================== *
 *                       Setup                        *
 * ================================================== */

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

void setup()
{
    Packet.begin(baud, node);
    
/* ---------------- Auto Setup start ---------------- */
/*                                                    */
    
/* ----- ACCEL setup ----- */
    Wire.begin();
    
    Serial.println("Initializing I2C devices...");
    accelgyro.initialize();
    
    Serial.println("Testing device connections...");
    Serial.println(accelgyro.testConnection() ? "MPU9250 connection successful" : "MPU9250 connection failed");
    
    delay(1000);
    
    //Mxyz_init_calibrated();

/*                                                    */
/* ----------------- Auto Setup end ----------------- */
    
    handshake();
}

/* ================================================== *
 *                  Loop and Serial                   *
 * ================================================== */

void loop()
{
/* ----------------- Auto Loop start ---------------- */
/*                                                    */
        
/* ----- ACCEL loop ----- */
    accelgyro.getMotion9(&accel_int16[0], &accel_int16[1], &accel_int16[2],
                         &gyro_int16[0], &gyro_int16[1], &gyro_int16[2],
                         &magnet_dummy, &magnet_dummy, &magnet_dummy);

        
/* ----- MAGNET loop ----- */
    I2C_M.writeByte(MPU9150_RA_MAG_ADDRESS, 0x0A, 0x01); //enable the magnetometer
    delay(10);
    I2C_M.readBytes(MPU9150_RA_MAG_ADDRESS, MPU9150_RA_MAG_XOUT_L,
                    mag_data_length, magnet_uint8);

/*                                                    */
/* ------------------ Auto Loop end ----------------- */
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

/*
 SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent()
{
    /* ---------------- Read Serial ----------------- */
    int result = Packet.readSerialData();
    // if result == 0, misformed packet, don't do anything
    if (result == 1)
    {
        command_id = Packet.getCommandID();
        payload = Packet.getPayload();
        
        while (Serial.read() > 0) {  }
        Serial.flush();
    }
    else if (result == 2)
    {
/* ------------------- Serial start ----------------- */
/*                                                    */
            
/* ----- ACCEL serial ----- */
        if (command_id == ACCEL_ID)
        {
            int16_to_uint8(accel_int16, data_length, accel_uint8);
            
            Packet.sendDataArray(accel_uint8, data_length * 2);

        }

            
/* ----- GYRO serial ----- */
        if (command_id == GYRO_ID)
        {
            int16_to_uint8(gyro_int16, data_length, gyro_uint8);
            
            Packet.sendDataArray(gyro_uint8, data_length * 2);

        }

            
/* ----- MAGNET serial ----- */
        if (command_id == MAGNET_ID)
        {
            Packet.sendDataArray(magnet_uint8, mag_data_length);

        }

/*                                                    */
/* -------------------- Serial end ------------------ */
    }
}
