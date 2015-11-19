#include <Wire.h>
#include <DueTimer.h>
#include <Adafruit_GPS.h>

#define MPU_ENABLE

#ifdef MPU_ENABLE

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

#endif

#define mySerial Serial1
Adafruit_GPS GPS(&mySerial);
#define GPSECHO  false
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy


// Initializations
void setup()
{
    Serial.begin(115200);
    
#ifdef MPU_ENABLE
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
    
    
    // Store initial time
    ti=millis();
#endif
    
    GPS.begin(9600);
    mySerial.begin(9600);
    GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
    GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
    GPS.sendCommand(PGCMD_ANTENNA);
#ifdef __arm__
    usingInterrupt = false;  //NOTE - we don't want to use interrupts on the Due
#else
    useInterrupt(true);
#endif
    delay(1000);
    // Ask for firmware version
    mySerial.println(PMTK_Q_RELEASE);
}

#ifdef __AVR__
// Interrupt is called once a millisecond, looks for any new GPS data, and stores it
SIGNAL(TIMER0_COMPA_vect) {
    char c = GPS.read();
    // if you want to debug, this is a good time to do it!
#ifdef UDR0
    if (GPSECHO)
        if (c) UDR0 = c;  
    // writing direct to UDR0 is much much faster than Serial.print 
    // but only one character can be written at a time. 
#endif
}

void useInterrupt(boolean v) {
    if (v) {
        // Timer0 is already used for millis() - we'll just interrupt somewhere
        // in the middle and call the "Compare A" function above
        OCR0A = 0xAF;
        TIMSK0 |= _BV(OCIE0A);
        usingInterrupt = true;
    } else {
        // do not call the interrupt function COMPA anymore
        TIMSK0 &= ~_BV(OCIE0A);
        usingInterrupt = false;
    }
}
#endif //#ifdef__AVR__

#ifdef MPU_ENABLE

// Counter
long int cpt=0;

void callback()
{ 
    intFlag=true;
    digitalWrite(13, digitalRead(13) ^ 1);
}

#endif

uint32_t timer = millis();

// Main loop, read and display data
void loop()
{
#ifdef MPU_ENABLE
    //    if (Serial.read() == 'c') {
    while (!intFlag);
    intFlag=false;
    //        
    //        // Display time
    Serial.print (millis()-ti,DEC);
    Serial.print ("\t");
    
    
    // _______________
    // ::: Counter :::
    
    // Display data counter
    //  Serial.print (cpt++,DEC);
    //  Serial.print ("\t");
    
    
    
    // ____________________________________
    // :::  accelerometer and gyroscope ::: 
    
    // Read accelerometer and gyroscope
    uint8_t Buf[14];
    I2Cread(MPU9250_ADDRESS,0x3B,14,Buf);
    
    // Create 16 bits values from 8 bits data
    
    // Accelerometer
    int16_t ax=-(Buf[0]<<8 | Buf[1]);
    int16_t ay=-(Buf[2]<<8 | Buf[3]);
    int16_t az=Buf[4]<<8 | Buf[5];
    
    // Gyroscope
    int16_t gx=-(Buf[8]<<8 | Buf[9]);
    int16_t gy=-(Buf[10]<<8 | Buf[11]);
    int16_t gz=Buf[12]<<8 | Buf[13];
    
    // Display values
    
    // Accelerometer
    Serial.print (ax,DEC); 
    Serial.print ("\t");
    Serial.print (ay,DEC);
    Serial.print ("\t");
    Serial.print (az,DEC);  
    Serial.print ("\t");
    
    // Gyroscope
    Serial.print (gx,DEC); 
    Serial.print ("\t");
    Serial.print (gy,DEC);
    Serial.print ("\t");
    Serial.print (gz,DEC);  
    Serial.print ("\t");
    
    
    // _____________________
    // :::  Magnetometer ::: 
    
    
    // Read register Status 1 and wait for the DRDY: Data Ready
    
    uint8_t ST1;
    do
    {
        I2Cread(MAG_ADDRESS,0x02,1,&ST1);
    }
    while (!(ST1&0x01));
    
    // Read magnetometer data  
    uint8_t Mag[7];  
    I2Cread(MAG_ADDRESS,0x03,7,Mag);
    
    
    // Create 16 bits values from 8 bits data
    
    // Magnetometer
    int16_t mx=-(Mag[3]<<8 | Mag[2]);
    int16_t my=-(Mag[1]<<8 | Mag[0]);
    int16_t mz=-(Mag[5]<<8 | Mag[4]);
    
    
    // Magnetometer
    Serial.print (mx+200,DEC); 
    Serial.print ("\t");
    Serial.print (my-70,DEC);
    Serial.print ("\t");
    Serial.print (mz-700,DEC);  
    Serial.print ("\t");
    
    
    
    // End of line
    Serial.println("");
//    delay(3);
#endif
    
    // in case you are not using the interrupt above, you'll
    // need to 'hand query' the GPS, not suggested :(
    if (! usingInterrupt) {
        // read data from the GPS in the 'main loop'
        char c = GPS.read();
        // if you want to debug, this is a good time to do it!
        if (GPSECHO)
            if (c) Serial.print(c);
    }
    
    // if a sentence is received, we can check the checksum, parse it...
    if (GPS.newNMEAreceived()) {
        // a tricky thing here is if we print the NMEA sentence, or data
        // we end up not listening and catching other sentences! 
        // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
        //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
        
        if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
            return;  // we can fail to parse a sentence in which case we should just wait for another
    }
    
    // if millis() or timer wraps around, we'll just reset it
    if (timer > millis())  timer = millis();
    
    Serial.print((int)GPS.fix); Serial.print(", "); 
    Serial.print((int)GPS.fixquality); Serial.print(", "); 
    Serial.print("(");
    Serial.print(GPS.latitude, 4); Serial.print(GPS.lat);
    Serial.print(", "); 
    Serial.print(GPS.longitude, 4); Serial.print(GPS.lon);
    Serial.print(")"); Serial.print(", "); 
    
    Serial.print(GPS.speed); Serial.print(", "); 
    Serial.print(GPS.angle); Serial.print(", "); 
    Serial.print(GPS.altitude); Serial.print(", "); 
    Serial.println((int)GPS.satellites);
    
    // approximately every 2 seconds or so, print out the current stats
//    if (millis() - timer > 2000) { 
//        timer = millis(); // reset the timer
//        
//        Serial.print("\nTime: ");
//        Serial.print(GPS.hour, DEC); Serial.print(':');
//        Serial.print(GPS.minute, DEC); Serial.print(':');
//        Serial.print(GPS.seconds, DEC); Serial.print('.');
//        Serial.println(GPS.milliseconds);
//        Serial.print("Date: ");
//        Serial.print(GPS.day, DEC); Serial.print('/');
//        Serial.print(GPS.month, DEC); Serial.print("/20");
//        Serial.println(GPS.year, DEC);
//        Serial.print("Fix: "); Serial.print((int)GPS.fix);
//        Serial.print(" quality: "); Serial.println((int)GPS.fixquality); 
//        if (GPS.fix) {
//            Serial.print("Location: ");
//            Serial.print(GPS.latitude, 4); Serial.print(GPS.lat);
//            Serial.print(", "); 
//            Serial.print(GPS.longitude, 4); Serial.println(GPS.lon);
//            
//            Serial.print("Speed (knots): "); Serial.println(GPS.speed);
//            Serial.print("Angle: "); Serial.println(GPS.angle);
//            Serial.print("Altitude: "); Serial.println(GPS.altitude);
//            Serial.print("Satellites: "); Serial.println((int)GPS.satellites);
//        }
//    }
}

