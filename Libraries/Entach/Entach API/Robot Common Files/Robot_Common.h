
// Entach_Common.h #include
#include "C:\Users\Robotc\Google Drive\2014 - 2015\Ben's Hit-by-a-Bus Folder\Entach API\Entach_Common.h"

// Sensor Includes

//Other #includes
#include "JoystickDriver.c"

//--------------------------------------------------------------------
//                      Variable Initialization
//--------------------------------------------------------------------

void initializeEntachVariables()
{
    rtp = 22.225; // Entach Trackball Parallel Radius
    rto = 6.9; // Entach Trackball Orthogonal Radius
    rp = 22.225; // Entach Parallel Radius
    encoderToCM = 0.01631957538934283120329631957539; // in cm
    maximumRobotSpeed = 7; // in cm / sec
    
    doesRobotStrafe = true;
}

//--------------------------------------------------------------------
//                      Encoder Management methods
//--------------------------------------------------------------------

void resetEntachEncoders()
{
//    nMotorEncoder[motor1] = 0;
//    nMotorEncoder[motor3] = 0;
//    nMotorEncoder[motor4] = 0;
}

task encoderEntachReadout()
{
    while (true)
    {
//        encoderEntachTrackballParallel    = nMotorEncoder[motor3];
//        encoderEntachTrackballOrthogonal  = nMotorEncoder[motor4];
//        encoderEntachParallel             = -nMotorEncoder[motor1];
    }
}

//--------------------------------------------------------------------
//                   Obstacle Detection Sensor methods
//--------------------------------------------------------------------

task updateObstacleSensors()
{
    while (true)
    {
//        obstacleReadingLeft  = SensorValue[ultrasonicLeft];
//        obstacleReadingRight = SensorValue[ultrasonicRight];
    }
}

//--------------------------------------------------------------------
//                         Motor drive methods
//--------------------------------------------------------------------

void stopMotors()
{
    // Stopped Implementation

    motorsStopped = true;
}

void driveForward(int inputSpeed)
{
    // Forward Implementation

    motorsStopped = false;
}

void driveBackward(int inputSpeed)
{
    // Backward Implementation

    motorsStopped = false;
}

void driveLeft(int inputSpeed)
{
    // Left Implementation

    motorsStopped = false;
}

void driveRight(int inputSpeed)
{
    // Right Implementation

    motorsStopped = false;
}

void rotateLeft(int inputSpeed)
{
    // Rotate Left Implementation

    motorsStopped = false;
}

void rotateRight(int inputSpeed)
{
    // Rotate Right Implementation

    motorsStopped = false;
}

void driveWithStrafingVelocity (float angleRadians, int maxMotorSpeed)
{
    //Based on the findings from "Model for Omnibase Strafing.numbers"
    //motor[motor1] = sin(angleRadians + 1 * PI / 4) * maxMotorSpeed;
    //motor[motor2] = sin(angleRadians + 3 * PI / 4) * maxMotorSpeed;
    //motor[motor3] = sin(angleRadians + 5 * PI / 4) * maxMotorSpeed;
    //motor[motor4] = sin(angleRadians + 7 * PI / 4) * maxMotorSpeed;

    motorsStopped = false;
}

//--------------------------------------------------------------------
//                             [...]
//--------------------------------------------------------------------



