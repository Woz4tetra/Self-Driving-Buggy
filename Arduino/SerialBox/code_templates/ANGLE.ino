
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

// Initial time
long int ti;
volatile bool intFlag=false;

// Counter
long int cpt=0;

void callback()
{ 
    intFlag=true;
    //digitalWrite(13, digitalRead(13) ^ 1);
}

/* --------------------- Setup ---------------------- */

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

/* ---------------------- Loop ---------------------- */

noInterrupts();

while (!intFlag);
intFlag=false;

// Read register Status 1 and wait for the DRDY: Data Ready

uint8_t ST1;
do {
    I2Cread(MAG_ADDRESS,0x02,1,&ST1);
}
while (!(ST1&0x01));

// Read magnetometer data  
uint8_t magnet_array[7];  
I2Cread(MAG_ADDRESS, 0x03, 7, magnet_array);

Packet.sendDataArray(magnet_array, 7);

interrupts();
