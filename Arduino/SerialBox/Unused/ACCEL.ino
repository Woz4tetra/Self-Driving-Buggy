
/* -------------------- Includes -------------------- */
#include <DueTimer.h>
#include <Wire.h>

/* -------------------- Globals --------------------- */

#define    MPU9250_ADDRESS            0x68
#define    MAG_ADDRESS                0x0C

#define    WHO_AM_I_MPU9250 0x75 // Should return 0x71

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

const int data_length = 7;

uint8_t Buf[data_length * 2];
uint8_t Mag[data_length];

uint8_t accel_data[data_length];
uint8_t gyro_data[data_length];
uint8_t magnet_data[data_length];

/* --------------------- Setup ---------------------- */
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

pinMode(13, OUTPUT);
Timer7.attachInterrupt(callback);  // attaches callback() as a timer overflow interrupt
Timer7.start(10000);         // initialize timer1, and set a 1/2 second period


// Store initial time
ti=millis();

uint8_t c;
I2Cread(MPU9250_ADDRESS, WHO_AM_I_MPU9250, 1, &c);  // Read WHO_AM_I register for MPU-9250
Serial.print("MPU9250 "); Serial.print("I AM "); Serial.print(c, HEX); Serial.print(" I should be "); Serial.println(0x71, HEX);

while (true)
{
    while (!intFlag);
    intFlag=false;
    
    I2Cread(MPU9250_ADDRESS, 0x3B, data_length * 2, Buf);
    
    uint8_t ST1;
    do {
        Serial.print("e");
        I2Cread(MAG_ADDRESS, 0x02, 1, &ST1);
    }
    while (!(ST1&0x01));
    
    I2Cread(MAG_ADDRESS, 0x03, data_length, Mag);
    
    int16_t mx=-(Mag[3]<<8 | Mag[2]);
    int16_t my=-(Mag[1]<<8 | Mag[0]);
    int16_t mz=-(Mag[5]<<8 | Mag[4]);
    
    Serial.print (mx+200,DEC);
    Serial.print ("\t");
    Serial.print (my-70,DEC);
    Serial.print ("\t");
    Serial.print (mz-700,DEC);
    Serial.print ("\t");
    Serial.println("");
    delay(100);
}

/* ---------------------- Loop ---------------------- */

//while (!intFlag);
//intFlag=false;
//
//I2Cread(MPU9250_ADDRESS, 0x3B, data_length * 2, Buf);
//
//uint8_t ST1;
//do {
//    I2Cread(MAG_ADDRESS, 0x02, 1, &ST1);
//}
//while (!(ST1&0x01));
//
//I2Cread(MAG_ADDRESS, 0x03, data_length, Mag);
//
//delay(50);

/* --------------------- Serial --------------------- */
for (int index = 0; index < data_length; index++) {
    accel_data[index] = Buf[index];
}

Packet.sendDataArray(accel_data, data_length);
