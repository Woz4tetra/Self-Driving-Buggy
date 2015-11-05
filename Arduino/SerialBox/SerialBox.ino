
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

//#include "I2Cdev.h"
//#include "MPU6050_6Axis_MotionApps20.h"
#include <Wire.h>
#include <DueTimer.h>
#include <Servo.h>
#include <Adafruit_GPS.h>

#include <SerialPacket.h>
#include <defines.h>

/* ================================================== *
 *                  Global constants                  *
 * ================================================== */


/* -------------- Command IDs start ----------------- */
/*                                                    */
#define ANGLE_ID 0x00
#define ENCODER_ID 0x01
#define GPS_ID 0x02
#define LED13_ID 0x03
#define SERVO_ID 0x04
/*                                                    */
/* --------------- Command IDs end ------------------ */

/* -------------- Serial Globals start -------------- */
/*                                                    */
SerialPacket Packet;

const int baud = 115200;
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
    //digitalWrite(13, digitalRead(13) ^ 1);
}


/* ----- ENCODER globals ----- */

bool is_in_range; //if true, trigger when we see out-of-range value
int last_rising_edge; //ms
volatile uint16_t distance; // counts of the encoder

#define HYST_TRIG_HIGH 950 //TODO: Tune these based on OBSERVED values
#define HYST_TRIG_LOW 850
//#define WHEEL_CIR (10.0 * PI)
#define ADC_POLLING_PERIOD_US 1000 //1KHz polling rate
/*
 The following back-of-the-envelope calcultaions indicate max speed:
 Assume we must poll at least 50x per revolution in order to 
 ALWAYS detect the magnet (this is conservative).
 Inches per Revolution = 31.415
 1KHz sample rate => 20 revolutions per second at 50 samples/rev
 628.3 inches per second => (approx) 37mph
 */

/* handler for timer interrupt during which ADC is polled */
void handler()
{
    int hall_value = analogRead(A0);
    
    if (is_in_range && (hall_value > HYST_TRIG_HIGH))
    {
        distance += 1; //WHEEL_CIR;
        is_in_range = false;
    }
    else if (!is_in_range && (hall_value <= HYST_TRIG_LOW)) {
        is_in_range = true;
    }
}


/* ----- GPS globals ----- */

// GPS power pin to Arduino Due 3.3V output.
// GPS ground pin to Arduino Due ground.
// For hardware serial 1 (recommended):
//   GPS TX to Arduino Due Serial1 RX pin 19
//   GPS RX to Arduino Due Serial1 TX pin 18
#define mySerial Serial1

Adafruit_GPS GPS(&mySerial);

const int gps_array_len = 8;
uint8_t gps_array[gps_array_len]; // 4 * 2, 2 float numbers

const int gps_float_array_len = 4;
float gps_float_array[gps_float_array_len];

// this keeps track of whether we're using the interrupt
// off by default!
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy

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

    void useInterrupt(boolean v)
    {
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
#endif


/* ----- LED13 globals ----- */

#define LED13_PIN 13


/* ----- SERVO globals ----- */

Servo servo1;


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
    
    

    /* ----- ENCODER setup ----- */
    
    /*disable interrupts to ensure we won't receive the first timer 
     or I2C interrupt before we are ready*/
    noInterrupts();
    
    pinMode(A0, INPUT);
    
    is_in_range = false; //make sure we don't start at > 0 distance
    distance = 0;
    
    Timer1.attachInterrupt(handler); //handler is a function pointer
    Timer1.start(ADC_POLLING_PERIOD_US);
    interrupts();
    
    

    /* ----- GPS setup ----- */
    
    // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
    GPS.begin(9600);
    mySerial.begin(9600);
    
    // Enable RMC (recommended minimum) and GGA (fix data) including altitude
    GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
    
    // Set the update rate
    GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
    
    // Request updates on antenna status, comment out to keep quiet
    GPS.sendCommand(PGCMD_ANTENNA);
    
    
    #ifdef __arm__
        usingInterrupt = false;  //NOTE - we don't want to use interrupts on the Due
    #else
        useInterrupt(true);
    #endif
    
    delay(1000);
    
    

    /* ----- LED13 setup ----- */
    
    pinMode(LED13_PIN, OUTPUT);
    
    

    /* ----- SERVO setup ----- */
    
    servo1.attach(3);
    servo1.write(0);
    
    

/*                                                    */
/* ----------------- Auto Setup end ----------------- */
    
    handshake();
}

/* ================================================== *
 *                  Loop and Serial                   *
 * ================================================== */

void loop()
{
    
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
/* ----------------- Auto Loop start ---------------- */
/*                                                    */
        /* ----- ANGLE loop ----- */
        
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
        

        /* ----- ENCODER loop ----- */
        
        noInterrupts();
        Packet.sendData16bit(command_id, distance);
        interrupts();

        /* ----- GPS loop ----- */
        
        // in case you are not using the interrupt above, you'll
        // need to 'hand query' the GPS, not suggested :(
        if (!usingInterrupt) {
            // read data from the GPS in the 'main loop'
            char c = GPS.read();
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
        
        
        gps_float_array[0] = GPS.latitude;
        gps_float_array[1] = GPS.longitude;
        gps_float_array[2] = GPS.speed;
        gps_float_array[3] = GPS.angle;
        
        for (int float_index = 0; float_index < gps_float_array_len; float_index++) {
            to_hex(gps_float_array[float_index], gps_array, float_index);
        }
        
        //gps_array[16] = (uint8_t)GPS.satellites;
        //gps_array[17] = (uint8_t)GPS.fixquality;
        
        Packet.sendDataArray(gps_array, gps_array_len);
        

        /* ----- LED13 loop ----- */
        
        digitalWrite(LED13_PIN, payload);
        Packet.sendCommandReply(command_id, payload);

        /* ----- SERVO loop ----- */
        
        servo1.write(payload);
        Packet.sendCommandReply(command_id, payload);

/*                                                    */
/* ------------------ Auto Loop end ----------------- */
    }
}
