/* -------------------- Includes -------------------- */

#include <Wire.h>
#include <DueTimer.h>

/* -------------------- Globals --------------------- */

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

volatile bool intFlag = false;

void callback()
{ 
    intFlag=true;
    digitalWrite(13, digitalRead(13) ^ 1);
}

uint8_t Buf[14];

uint8_t accel_array[6];

/* --------------------- Setup ---------------------- */

// Arduino initializations
Wire.begin();

//    Serial.println("type c to print data");

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

pinMode(13, OUTPUT);
Timer7.attachInterrupt(callback);  // attaches callback() as a timer overflow interrupt
Timer7.start(10000);         // initialize timer1, and set a 1/2 second period

/* ---------------------- Loop ---------------------- */

while (!intFlag);
intFlag=false;

// Read accelerometer and gyroscope
I2Cread(MPU9250_ADDRESS,0x3B,14,Buf);

/* --------------------- Serial --------------------- */

for (int index = 0; index < 6; index++) {
    accel_array[index] = Buf[index];
}

Packet.sendDataArray(accel_array, 6);
