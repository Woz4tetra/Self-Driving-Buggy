
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
 *  MPU6050 drivers (built-in ?)
 *  Wire.h libary (built-in)
 *  /ben_projects/Self-Driving\ Buggy\ Rev.\ 6/board/test_serial.py
 *  
 */

#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#include "Wire.h"
#include "DueTimer.h"
#include <Servo.h>
#include <Adafruit_GPS.h>

#include "SerialPacket.h"
#include "defines.h"

/* Command IDs start */
#define ACCELGYRO_ID 0x00
#define GPS_ID 0x01
#define ENCODER_ID 0x02
#define SERVO_ID 0x03
#define LED13_ID 0x04
/* Command IDs end */

/* Enables start */
#define ENABLE_SERVO
#define ENABLE_GPS
#define ENABLE_ACCEL_SIMPLE
//#define ENABLE_ACCEL
#define ENABLE_ENCODER
/* Enables end */

/* Serial Packet Globals */
uint8_t command_id = 0;
uint8_t payload = 0;

SerialPacket Packet;

/* LED 13 Globals */

#define LED13_PIN 13

/* Servo Globals */
#ifdef ENABLE_SERVO
Servo servo1;
#endif

/* GPS Globals */
#ifdef ENABLE_GPS
// GPS power pin to Arduino Due 3.3V output.
// GPS ground pin to Arduino Due ground.
// For hardware serial 1 (recommended):
//   GPS TX to Arduino Due Serial1 RX pin 19
//   GPS RX to Arduino Due Serial1 TX pin 18
#define mySerial Serial1

Adafruit_GPS GPS(&mySerial);

uint8_t gps_array[8]; // 4 * 2, 2 float numbers | old: 4 * 4 + 2 * 1, 4 float numbers and 2 int numbers
// sending floats: longitude, latitude, speed, angle
// sendings ints: satellites, fix quality

float gps_float_array[4];

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

#endif

/* IMU Globals */
#ifdef ENABLE_ACCEL_SIMPLE
MPU6050 accelgyro;

int16_t ax, ay, az;
int16_t gx, gy, gz;

uint8_t accelgyro_array[12];
#endif

#ifdef ENABLE_ACCEL
MPU6050 mpu;

uint8_t accelgyro_array[12]; // 4 * 3, 3 float numbers

// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}

#endif

/* Distance encoder Globals */
#ifdef ENABLE_ENCODER
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
#endif


void setup()
{
    pinMode(LED13_PIN, OUTPUT);
    
    Packet.begin(115200, 2);
    
#ifdef ENABLE_ENCODER
    /*disable interrupts to ensure we won't receive the first timer 
     or I2C interrupt before we are ready*/
    noInterrupts();
    
    pinMode(A0, INPUT);
    
    is_in_range = false; //make sure we don't start at > 0 distance
    distance = 0;
    
    Timer1.attachInterrupt(handler); //handler is a function pointer
    Timer1.start(ADC_POLLING_PERIOD_US);
    interrupts();
#endif
    
    
#ifdef ENABLE_GPS
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
    
#endif
    
    
#ifdef ENABLE_SERVO
    servo1.attach(2);
    servo1.write(0);
#endif
    
    
#ifdef ENABLE_ACCEL_SIMPLE
Wire.begin(); //I2C library
accelgyro.initialize(); //IMU library

#endif

#ifdef ENABLE_ACCEL
    // join I2C bus (I2Cdev library doesn't do this automatically)
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin();
//    TWBR = 24; // 400kHz I2C clock (200kHz if CPU is 8MHz)
#elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400, true);
#endif

    // initialize device
    Serial.println(F("Initializing I2C devices..."));
    mpu.initialize();

    // verify connection
    Serial.println(F("Testing device connections..."));
    Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

    // wait for ready
//    Serial.println(F("\nSend any character to begin DMP programming and demo: "));
//    while (Serial.available() && Serial.read()); // empty buffer
//    while (!Serial.available());                 // wait for data
    while (Serial.available() && Serial.read()); // empty buffer again

    // load and configure the DMP
    Serial.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(220);
    mpu.setYGyroOffset(76);
    mpu.setZGyroOffset(-85);
    mpu.setZAccelOffset(1788); // 1688 factory default for my test chip

    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // turn on the DMP, now that it's ready
        Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

        // enable Arduino interrupt detection
        Serial.println(F("Enabling interrupt detection (Arduino external interrupt 0)..."));
        attachInterrupt(0, dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();

        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        Serial.println(F("DMP ready! Waiting for first interrupt..."));
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    }
    else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }
#endif
    
    handshake();
}

void loop()
{
//    delay(3);
}

/*
 SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent()
{
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
        if (command_id == LED13_ID)
        {
            digitalWrite(LED13_PIN, payload);
            Packet.sendCommandReply(command_id, payload);
        }
#ifdef ENABLE_ACCEL
        else if (command_id == ACCELGYRO_ID)
        {
            // if programming failed, don't try to do anything
            if (!dmpReady) return;

            // wait for MPU interrupt or extra packet(s) available
            while (!mpuInterrupt && fifoCount < packetSize) {
                // other program behavior stuff here
                // .
                // .
                // .
                // if you are really paranoid you can frequently test in between other
                // stuff to see if mpuInterrupt is true, and if so, "break;" from the
                // while() loop to immediately process the MPU data
                // .
                // .
                // .
            }

            // reset interrupt flag and get INT_STATUS byte
            mpuInterrupt = false;
            mpuIntStatus = mpu.getIntStatus();

            // get current FIFO count
            fifoCount = mpu.getFIFOCount();

            // check for overflow (this should never happen unless our code is too inefficient)
            if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
                // reset so we can continue cleanly
                mpu.resetFIFO();
                Serial.println(F("FIFO overflow!"));

                // otherwise, check for DMP data ready interrupt (this should happen frequently)
            }
            else if (mpuIntStatus & 0x02) {
                // wait for correct available data length, should be a VERY short wait
                while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();

                // read a packet from FIFO
                mpu.getFIFOBytes(fifoBuffer, packetSize);

                // track FIFO count here in case there is > 1 packet available
                // (this lets us immediately read more without waiting for an interrupt)
                fifoCount -= packetSize;

                mpu.dmpGetQuaternion(&q, fifoBuffer);
                mpu.dmpGetGravity(&gravity, &q);
                mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
            }

            for (int float_index = 0; float_index < 2; float_index++) {
                to_hex(ypr[float_index], accelgyro_array, float_index);
            }

            Packet.sendDataArray(accelgyro_array, 12);
        }
#endif

#ifdef ENABLE_ACCEL_SIMPLE
        else if (command_id == ACCELGYRO_ID)
        {
            //ax = random(-0x8000, 0x8000 - 1);
            //ay = random(-0x8000, 0x8000 - 1);
            //az = random(-0x8000, 0x8000 - 1);
            //gx = random(-0x8000, 0x8000 - 1);
            //gy = random(-0x8000, 0x8000 - 1);
            //gz = random(-0x8000, 0x8000 - 1);

            accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
            accelgyro_array[0] = ax >> 8;
            accelgyro_array[1] = ax & 0xffff;
            accelgyro_array[2] = ay >> 8;
            accelgyro_array[3] = ay & 0xffff;
            accelgyro_array[4] = az >> 8;
            accelgyro_array[5] = az & 0xffff;

            accelgyro_array[6] = gx >> 8;
            accelgyro_array[7] = gx & 0xffff;
            accelgyro_array[8] = gy >> 8;
            accelgyro_array[9] = gy & 0xffff;
            accelgyro_array[10] = gz >> 8;
            accelgyro_array[11] = gz & 0xffff;
            Packet.sendDataArray(accelgyro_array, 12);
        }
#endif
        
#ifdef ENABLE_ENCODER
        else if (command_id == ENCODER_ID)
        {
            noInterrupts();
            Packet.sendData16bit(command_id, distance);
            interrupts();
        }
#endif
        
#ifdef ENABLE_SERVO
        else if (command_id == SERVO_ID)
        {
            servo1.write(payload);
            Packet.sendCommandReply(command_id, payload);
        }
#endif
        
#ifdef ENABLE_GPS
        else if (command_id == GPS_ID)
        {
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
            //gps_float_array[2] = GPS.speed;
            //gps_float_array[3] = GPS.angle;
            
            for (int float_index = 0; float_index < 2; float_index++) {
                to_hex(gps_float_array[float_index], gps_array, float_index);
            }
            
            //gps_array[16] = (uint8_t)GPS.satellites;
            //gps_array[17] = (uint8_t)GPS.fixquality;
            
            Packet.sendDataArray(gps_array, 8);
        }
#endif
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

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}