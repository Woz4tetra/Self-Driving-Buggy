#pragma config(Hubs,  S1, HTMotor,  HTMotor,  none,     none)
#pragma config(Sensor, S1,     ,               sensorI2CMuxController)
#pragma config(Sensor, S2,     HTIRS2,         sensorI2CCustom)
#pragma config(Sensor, S4,     lightSensor2,   sensorLightActive)
#pragma config(Motor,  mtr_S1_C1_1,     motor1,        tmotorTetrix, openLoop, encoder)
#pragma config(Motor,  mtr_S1_C1_2,     motor2,        tmotorTetrix, openLoop)
#pragma config(Motor,  mtr_S1_C2_1,     motor3,        tmotorTetrix, openLoop, encoder)
#pragma config(Motor,  mtr_S1_C2_2,     motor4,        tmotorTetrix, openLoop, encoder)

//Robot #includes
#include "C:\Users\Woz4tetra\Google Drive\2014 - 2015\Ben's Hit-by-a-Bus Folder\Entach API\Control Files\Robot_Common.h"

//Other #includes

//--------------------------------------
//          Global Variables
//--------------------------------------

bool buttonsActive = false;
bool dPadActive = false;
bool rightJoystickActive = false;
bool leftJoystickActive = false;

//--------------------------------------
//      Place control methods here
//--------------------------------------

bool anyButtonsPressed()
{
    // if any buttons are pressed...
    if (joy1Btn(1) || joy1Btn(2) || joy1Btn(3) || joy1Btn(4) || joy1Btn(5) || joy1Btn(6) || joy1Btn(7) || joy1Btn(8) || joy1Btn(9) || joy1Btn(10) || joy1Btn(11) || joy1Btn(12))
    {
        return true;
    }
    else {
        return false;
    }
}

task updateJoystickSettings()
{
    while (true)
    {
        getJoystickSettings(joystick);
    }
}

task checkButtons()
{
    while (true)
    {
        if (anyButtonsPressed() == true)
        {

        }

        if (joy1Btn(1))
        {

        }
        else if (joy1Btn(2))
        {

        }
        else if (joy1Btn(3))
        {

        }
        else if (joy1Btn(4))
        {

        }
        else if (joy1Btn(5))
        {

        }
        else if (joy1Btn(6))
        {

        }
        else if (joy1Btn(7))
        {

        }
        else if (joy1Btn(8))
        {

        }
        else if (joy1Btn(9))
        {

        }
        else if (joy1Btn(10))
        {

        }
        else if (joy1Btn(11))
        {

        }
        else if (joy1Btn(12))
        {

        }
        else
        {
            buttonsActive = false;
        }
    }
}

task checkDpad()
{
    while (true)
    {
        if (joystick.joy1_TopHat != -1)
        {
            dPadActive = true;

            if (joystick.joy1_TopHat == 0)
            {
                
            }
            if (joystick.joy1_TopHat == 4)
            {
                
            }
            if (joystick.joy1_TopHat == 2)
            {
                
            }
            if (joystick.joy1_TopHat == 6)
            {
                
            }
        }
        else
        {
            dPadActive = false;
            stopMotors();
        }
    }
}

task checkRightJoystick()
{
    while (true)
    {
        if ( abs(joystick.joy1_x2) > 20)
        {
            rightJoystickActive = true;

            if (joystick.joy1_x2 > 20)
            {

            }
            else if (joystick.joy1_x2 < -20)
            {

            }
        }
        else if ( abs(joystick.joy1_y2) > 20)
        {
            rightJoystickActive = true;

            if (joystick.joy1_y2 > 20)
            {

            }
            else if (joystick.joy1_y2 < -20)
            {

            }
        }
        else
        {
            rightJoystickActive = false;
        }
    }
}

task checkLeftJoystick()
{
    while (true)
    {
        if ( abs(joystick.joy1_x1) > 20)
        {
            leftJoystickActive = true;

            if (joystick.joy1_x1 > 20)
            {

            }
            else if (joystick.joy1_x1 < -20)
            {

            }
        }
        else if ( abs(joystick.joy1_y1) > 20)
        {
            leftJoystickActive = true;

            if (joystick.joy1_y1 > 20)
            {

            }
            else if (joystick.joy1_y1 < -20)
            {

            }
        }
        else
        {
            leftJoystickActive = false;
        }
    }
}

task main()
{
    //-------------------------------------
    //              Variables
    //-------------------------------------
    
    initializeEntachVariables();
    
    //-------------------------------------
    //      Entach Initializations
    //-------------------------------------
    
    clearDebugStream();
    
    resetEntachEncoders();
    StartTask(encoderEntachReadout);
    
    StartTask(updateEncoderSpeeds);
    StartTask(updatePosition);
    StartTask(updateObstacleSensors);
    
    StartTask(accelerationSetter);
    
    //-------------------------------------
    //      Controller Initializations
    //-------------------------------------
    
    StartTask(updateJoystickSettings);
    
    StartTask(checkButtons);
    StartTask(checkDpad);
    StartTask(checkRightJoystick);
    StartTask(checkLeftJoystick);

    //-------------------------------------
    //      Robot Initializations
    //-------------------------------------

    // entachServosDown();

    //-------------------------------------
    //			Temporary tests
    //-------------------------------------

    //StopAllTasks();

    //-------------------------------------
    //         Manual Control code
    //-------------------------------------
    
    while (true) {
        
    }
    
    //-------------------------------------
    //             End Program
    //-------------------------------------

    // entachServosUp();

    wait1Msec(100);
    //PlaySoundFile("SM64StageClear.rso");

    while(bSoundActive) { }
    wait1Msec(100);

    StopAllTasks();
}
