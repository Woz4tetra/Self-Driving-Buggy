
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
#include <DueTimer.h>
#include <Wire.h>

/*                                                    */
/* ----------------- Includes end ------------------- */

/* -------------- Command IDs start ----------------- */
/*                                                    */
#define ANGLE_ID 0x00
#define LED13_ID 0x01
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

/* ----- ANGLE globals ----- */
#define    MPU9250_ADDRESS            0x68
#define    MAG_ADDRESS                0x0C

#define    GYRO_FULL_SCALE_250_DPS    0x00  
#define    GYRO_FULL_SCALE_500_DPS    0x08
#define    GYRO_FULL_SCALE_1000_DPS   0x10
#define    GYRO_FULL_SCALE_2000_DPS   0x18

#define    ACC_FULL_SCALE_2_G        0x00  
#define    ACC_FULL_SCALE_4_G        0x08
#define    ACC_FULL_SCALE_8_G        0x10
#define    ACC_FULL_SCALE_16_G       0x18



// This function read Nbytes bytes from I2C device at address Address. 
// Put read bytes starting at register Register in the Data array. 
void I2Cread(uint8_t Address, uint8_t Register, uint8_t Nbytes, uint8_t* Data)
{
    // Set register address
    Wire.beginTransmission(Address);
    Wire.write(Register);
    Wire.endTransmission();
    
    // Read Nbytes
    Wire.requestFrom(Address, Nbytes); 
    uint8_t index=0;
    while (Wire.available())
        Data[index++]=Wire.read();
}


// Write a byte (Data) in device (Address) at register (Register)
void I2CwriteByte(uint8_t Address, uint8_t Register, uint8_t Data)
{
    // Set register address
    Wire.beginTransmission(Address);
    Wire.write(Register);
    Wire.write(Data);
    Wire.endTransmission();
}



// Initial time
long int ti;
volatile bool intFlag=false;

// Counter
long int cpt=0;

void callback()
{ 
    intFlag=true;
    digitalWrite(13, digitalRead(13) ^ 1);
}

uint8_t angle_data[7];

/* ----- LED13 globals ----- */
#define LED13_PIN 13
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
    
/* ----- ANGLE setup ----- */
    // Arduino initializations
    Wire.begin();
    
    // Set accelerometers low pass filter at 5Hz
    I2CwriteByte(MPU9250_ADDRESS,29,0x06);
    // Set gyroscope low pass filter at 5Hz
    I2CwriteByte(MPU9250_ADDRESS,26,0x06);
    
    
    // Configure gyroscope range
    I2CwriteByte(MPU9250_ADDRESS,27,GYRO_FULL_SCALE_1000_DPS);
    // Configure accelerometers range
    I2CwriteByte(MPU9250_ADDRESS,28,ACC_FULL_SCALE_4_G);
    // Set by pass mode for the magnetometers
    I2CwriteByte(MPU9250_ADDRESS,0x37,0x02);
    
    // Request continuous magnetometer measurements in 16 bits
    I2CwriteByte(MAG_ADDRESS,0x0A,0x16);
    
    Timer7.attachInterrupt(callback);  // attaches callback() as a timer overflow interrupt
    Timer7.start(10000);         // initialize timer1, and set a 1/2 second period
    
    // Store initial time
    ti=millis();

    
/* ----- LED13 setup ----- */
    pinMode(LED13_PIN, OUTPUT);

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
        
/* ----- ANGLE loop ----- */
    while (!intFlag);
    intFlag=false;
    
    // ____________________________________
    // :::  accelerometer and gyroscope ::: 
    
    // Read accelerometer and gyroscope
    //uint8_t Buf[14];
    //I2Cread(MPU9250_ADDRESS,0x3B,14,Buf);
    
    // Create 16 bits values from 8 bits data
    
    // Accelerometer
    //int16_t ax=-(Buf[0]<<8 | Buf[1]);
    //int16_t ay=-(Buf[2]<<8 | Buf[3]);
    //int16_t az=Buf[4]<<8 | Buf[5];
    //
    //// Gyroscope
    //int16_t gx=-(Buf[8]<<8 | Buf[9]);
    //int16_t gy=-(Buf[10]<<8 | Buf[11]);
    //int16_t gz=Buf[12]<<8 | Buf[13];
    
    
    // _____________________
    // :::  Magnetometer ::: 
    
    
    // Read register Status 1 and wait for the DRDY: Data Ready
    
    uint8_t ST1;
    do
    {
        I2Cread(MAG_ADDRESS, 0x02, 1, &ST1);
    }
    while (!(ST1&0x01));
    
    // Read magnetometer data  
    //uint8_t Mag[7];  
    I2Cread(MAG_ADDRESS, 0x03, 7, angle_data);
    
    
    // Create 16 bits values from 8 bits data
    
    // Magnetometer
    //int16_t mx=-(Mag[3]<<8 | Mag[2]);
    //int16_t my=-(Mag[1]<<8 | Mag[0]);
    //int16_t mz=-(Mag[5]<<8 | Mag[4]);

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
            
/* ----- ANGLE serial ----- */
        if (command_id == ANGLE_ID)
        {
            Packet.sendDataArray(angle_data, 7);

        }

            
/* ----- LED13 serial ----- */
        if (command_id == LED13_ID)
        {
            digitalWrite(LED13_PIN, payload);
            Packet.sendCommandReply(command_id, payload);

        }

/*                                                    */
/* -------------------- Serial end ------------------ */
    }
}
