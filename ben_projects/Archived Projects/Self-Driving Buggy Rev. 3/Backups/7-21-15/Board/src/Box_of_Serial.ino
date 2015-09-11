
#include <I2Cdev.h>
//#include <Servo.h>
#include <AFMotor.h> // Occupies all pins except 8, 6, 3, 2, 1, 0
#include <MPU6050_6Axis_MotionApps20.h>
#include <HMC5883L.h>
#include <NewPing.h>
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
#include <Wire.h>
#endif

/* --- Button variables --- */
#define BUTTON_PIN_1 3

/* --- Sonar variables --- */
#define SONAR_TRIGGER_PIN_1  8
#define SONAR_ECHO_PIN_1     6
#define MAX_DISTANCE 200

NewPing sonar1(SONAR_TRIGGER_PIN_1, SONAR_ECHO_PIN_1, MAX_DISTANCE);


/* --- DC Motor variables --- */
uint8_t motorSpeeds[4];
AF_DCMotor motor1(1);
//AF_DCMotor motor2(2);
//AF_DCMotor motor3(3);
//AF_DCMotor motor4(4);

/* --- Stepper Motor variables --- */
//AF_Stepper stepper1(48, 1);
//AF_Stepper stepper2(48, 2);

/* --- Magnetometer variables --- */
HMC5883L mag;
int16_t mx, my, mz;

/* --- IMU variables --- */
MPU6050 mpu;

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

float time0;
float dt;

volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady() {
    mpuInterrupt = true;
}


/* -------------------------------------------------- */
/*                      Setup                         */
/* -------------------------------------------------- */
void setup()
{
    /* --- Setup I2C --- */
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    Wire.begin();
    TWBR = 24; // 400kHz I2C clock (200kHz if CPU is 8MHz)
#elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
    Fastwire::setup(400, true);
#endif
    
    /* --- Initialize Serial --- */
    Serial.begin(38400);
    
    /* --- Initialize Buttons --- */
    pinMode(BUTTON_PIN_1, INPUT);
    
    
    /* --- Configure IMU --- */
    
    // test the connection to the I2C bus, sometimes it doesn't connect
    // keep trying to connect to I2C bus if we get an error
    boolean error = true;
    int failCount = 0;
    while (error)
    {
        Wire.beginTransmission(0x68);
        error = Wire.endTransmission(1); // if error = 0, we are properly connected
        if (error) { // if we aren't properly connected, try connecting again and loop
            Wire.begin();
            TWBR = 24; // 400kHz I2C clock
            failCount++;
        }
    }
    devStatus = mpu.dmpInitialize();
    
    // as calculated by MPU6050_calibration.ino:
    mpu.setXAccelOffset(-5403);
    mpu.setYAccelOffset(105);
    mpu.setZAccelOffset(1165);
    mpu.setXGyroOffset(58);
    mpu.setYGyroOffset(-71);
    mpu.setZGyroOffset(28);
    
    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // turn on the DMP, now that it's ready
        mpu.setDMPEnabled(true);
        
        // enable Arduino interrupt detection
        attachInterrupt(0, dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();
        
        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        dmpReady = true;
        
        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    }
    else
    {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }
    
    /* --- Initialize Magnetometer --- */
    mag.initialize();
    
    /* --- Setup serial handshake with PC (establish serial connection) --- */
    establishContact();
    
    /* --- Initialize IMU timing --- */
    time0 = millis();
}


/* -------------------------------------------------- */
/*                       Loop                         */
/* -------------------------------------------------- */
void loop()
{
    // If IMU's dmp doesn't initialize, don't run
    if (!dmpReady) return;
    
    updateIMU();
    
    // Update IMU timing variable
    dt = millis() - time0;
    time0 = millis();
    
    if (Serial.available() > 0)
    {
        // Read selector byte from serial
        char incomingByte = Serial.read();
        
        // Delay for the motors and IMU sensor
        delay(5);
        
        if (incomingByte == 'a')  // Send accel & gyro data over serial
        {
            // Write roll, pitch, and yaw
            Serial.print(ypr[2] * 180/M_PI); Serial.print(',');
            Serial.print(ypr[1] * 180/M_PI); Serial.print(',');
            Serial.print(ypr[0] * 180/M_PI); Serial.print(',');
            
            // Write x, y, z acceleration
            Serial.print(aaWorld.x); Serial.print(',');
            Serial.print(aaWorld.y); Serial.print(',');
            Serial.print(aaWorld.z); Serial.print(',');
            
            // Write magnetometer
            Serial.print(mx); Serial.print(',');
            Serial.print(my); Serial.print(',');
            Serial.print(mz); Serial.print(',');
            
            // Write dt (difference between measurements)
            Serial.print(dt); Serial.print('\n');
        }
        else if (incomingByte == 'b')
        {
            
        }
        else if (incomingByte == 'c')  // Run a dc motor forward (pin and speed specified in next serial reads)
        {
            // Read pin selector
            uint8_t motorPin = (uint8_t)Serial.read();
            
            // Read speed
            motorSpeeds[motorPin - 1] = (uint8_t)Serial.read();
            
            if (motorPin == 1) {
                motor1.run(FORWARD);
                motor1.setSpeed(motorSpeeds[motorPin - 1]);
            }
        }
        else if (incomingByte == 'd')  // Run a dc motor backwards
        {
            uint8_t motorPin = (uint8_t)Serial.read();
            motorSpeeds[motorPin - 1] = (uint8_t)Serial.read();
            
            if (motorPin == 1) {
                motor1.run(BACKWARD);
                motor1.setSpeed(motorSpeeds[motorPin - 1]);
            }
        }
        else if (incomingByte == 'e')  // Stop a dc motor
        {
            uint8_t motorPin = (uint8_t)Serial.read();
            
            if (motorPin == 1) {
                motor1.run(BRAKE);
                motor1.setSpeed(0);
            }
        }
        else if (incomingByte == 'f')  // Print a button status to serial
        {
            uint8_t buttonPin = (uint8_t)Serial.read();
            
            Serial.print(digitalRead(buttonPin));
            Serial.print('\n');
        }
        else if (incomingByte == 'g')
        {
            uint8_t sonarNumber = (uint8_t)Serial.read();
            
            delay(33);
            if (sonarNumber == 1) {
                unsigned int usec = sonar1.ping();
                Serial.print(usec / US_ROUNDTRIP_CM); // centimeters
            }
            Serial.print('\n');
        }
        else if (incomingByte == 'z')  // Program exit command
        {
            motor1.run(RELEASE);
        }
    }
}

void updateIMU()
{
    mpuInterrupt = false;
    mpuIntStatus = mpu.getIntStatus();
    
    fifoCount = mpu.getFIFOCount();
    
    if ((mpuIntStatus & 0x10) || fifoCount == 1024) {
        // reset so we can continue cleanly
        mpu.resetFIFO();
    }
    else if (mpuIntStatus & 0x02)
    {
        while (fifoCount < packetSize) fifoCount = mpu.getFIFOCount();
        
        mpu.getFIFOBytes(fifoBuffer, packetSize);
        
        fifoCount -= packetSize;
        
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
    }
    
    mx = mag.getHeadingX();
    my = mag.getHeadingY();
    mz = mag.getHeadingZ();
}

void establishContact()
{
    while (Serial.available() <= 0)
    {
        Serial.print("R");  // Send ready flag
        delay(300);
    }
    
    Serial.flush();
    delay(10);
}
