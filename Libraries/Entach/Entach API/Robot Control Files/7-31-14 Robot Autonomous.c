#pragma config(Hubs,  S1, HTMotor,  HTMotor,  none,     none)
#pragma config(Sensor, S1,     ,               sensorI2CMuxController)
#pragma config(Sensor, S2,     HTIRS2,         sensorI2CCustom)
#pragma config(Sensor, S4,     lightSensor2,   sensorLightActive)
#pragma config(Motor,  mtr_S1_C1_1,     motor1,        tmotorTetrix, openLoop, encoder)
#pragma config(Motor,  mtr_S1_C1_2,     motor2,        tmotorTetrix, openLoop)
#pragma config(Motor,  mtr_S1_C2_1,     motor3,        tmotorTetrix, openLoop, encoder)
#pragma config(Motor,  mtr_S1_C2_2,     motor4,        tmotorTetrix, openLoop, encoder)

//Robot #includes
#include "C:\Users\Woz4tetra\Google Drive\2014 - 2015\Ben's Hit-by-a-Bus Folder\Entach API\Common Files\Robot_Common.h"

//Other #includes

//--------------------------------------------------------------------
//                          Global variables
//--------------------------------------------------------------------



//--------------------------------------------------------------------
//                       Method initializations
//--------------------------------------------------------------------



//--------------------------------------------------------------------
//                              Task main
//--------------------------------------------------------------------

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
    //      Robot Initializations
    //-------------------------------------

    // entachServosDown();

    //-------------------------------------
    //			Temporary tests
    //-------------------------------------

    //StopAllTasks();

    //-------------------------------------
    //			Autonomous code
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

//--------------------------------------------------------------------
//                       Method implementations
//--------------------------------------------------------------------
