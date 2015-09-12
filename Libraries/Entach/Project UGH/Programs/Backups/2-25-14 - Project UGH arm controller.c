#pragma config(Hubs,  S1, HTMotor,  HTServo,  none,     none)
#pragma config(Sensor, S2,     colorSensor,    sensorI2CCustom)
#pragma config(Sensor, S3,     sonarSensor,    sensorSONAR)
#pragma config(Sensor, S4,     eopdSensor,     sensorAnalogActive)
#pragma config(Motor,  mtr_S1_C1_1,     armBaseMotor,  tmotorTetrix, openLoop)
#pragma config(Motor,  mtr_S1_C1_2,     motorE,        tmotorTetrix, openLoop)
#pragma config(Servo,  srvo_S1_C2_1,    wristServo1,          tServoStandard)
#pragma config(Servo,  srvo_S1_C2_2,    servo2,               tServoNone)
#pragma config(Servo,  srvo_S1_C2_3,    clawServoRight,       tServoStandard)
#pragma config(Servo,  srvo_S1_C2_4,    clawServoLeft,        tServoStandard)
#pragma config(Servo,  srvo_S1_C2_5,    servo5,               tServoNone)
#pragma config(Servo,  srvo_S1_C2_6,    servo6,               tServoNone)
//*!!Code automatically generated by 'ROBOTC' configuration wizard               !!*//

#include "C:\Program Files (x86)\Robomatter Inc\ROBOTC Development Environment\Sample Programs\NXT\3rd Party Sensor Drivers\drivers\lego-ultrasound.h"
#include "C:\Program Files (x86)\Robomatter Inc\ROBOTC Development Environment\Sample Programs\NXT\3rd Party Sensor Drivers\drivers\hitechnic-colour-v2.h"
#include "C:\Program Files (x86)\Robomatter Inc\ROBOTC Development Environment\Sample Programs\NXT\3rd Party Sensor Drivers\drivers\hitechnic-eopd.h"


#include "JoystickDriver.c"

//--------------------------------------
//					Global Variables
//--------------------------------------

int sonarDistanceReading;
int eopdReading = 0;
int red;
int green;
int blue;


//--------------------------------------
//					Control methods
//--------------------------------------

void armTurretRight()
{
	motor[armBaseMotor] = 15;
}

void armTurretLeft()
{
	motor[armBaseMotor] = -15;
}

int openClawServos()
{
	servo[clawServoRight] = 0;
	servo[clawServoLeft] = 255;

	return 255;
}

int closeClawServos()
{
	servo[clawServoRight] = 255;
	servo[clawServoLeft] = 0;

	return 0;
}

//--------------------------------------
//					Autonomous hand methods
//--------------------------------------

void searchForBlocks()
{
	if (red > 200 && ( green > 100 && green < 160 ) && blue < 30)
	{	writeDebugStreamLine("Block found!!!"); }

	int distanceSample1 = 0;
	int distanceSample2 = 0;
	int distanceSample3 = 0;
	int distanceSample4 = 0;
	int distanceSample5 = 0;

	for (int counter = 0; counter < 5; counter++)
	{
		switch (counter)
		{
			case 1: distanceSample1 = sonarDistanceReading;
			case 2: distanceSample2 = sonarDistanceReading;
			case 3: distanceSample3 = sonarDistanceReading;
			case 4: distanceSample4 = sonarDistanceReading;
			case 5: distanceSample5 = sonarDistanceReading;
		}
	}

	int averageOfSamples = (distanceSample1 + distanceSample2 + distanceSample3 + distanceSample4 + distanceSample5)/5;
	writeDebugStreamLine("averageOfSamples: %i", averageOfSamples);

	if ( averageOfSamples > 10)
	{	writeDebugStreamLine("Edge found!!!"); }
}

//--------------------------------------
//								Tasks
//--------------------------------------

task updateJoystickSettings()
{
  while (true)
    getJoystickSettings(joystick);
}

task updateSensors()
{
	if (!HTCS2readRGB(colorSensor, red, green, blue))
	{
    nxtDisplayTextLine(4, "ERROR!!");
    wait1Msec(2000);
    StopAllTasks();
  }

  HTEOPDsetShortRange(eopdSensor);

	while (true)
	{
		HTCS2readRGB(colorSensor, red, green, blue);
		sonarDistanceReading = SensorValue[sonarSensor];
		eopdReading = HTEOPDreadProcessed(eopdSensor);
	}
}

void checkButtons()
{
    if (joy1Btn(1))
    {
			if (ServoValue[clawServoLeft] != openClawServos())
				openClawServos();
			else
				closeClawServos();

			wait1Msec(250);
    }
    else if (joy1Btn(2))
    {
			writeDebugStreamLine("colorSensor: %i, %i, %i", red, green, blue);
			writeDebugStreamLine("sonarDistanceReading: %i", sonarDistanceReading);

			wait1Msec(250);
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
    else
    {
			motor[armBaseMotor] = 0;
    }
}


task main()
{
	clearDebugStream();

	StartTask(updateJoystickSettings);
	StartTask(updateSensors);

	while (true)
	{
		writeDebugStreamLine("sonar\teopd\tr\tg\tb");
		writeDebugStreamLine("%i\t%i\t%i\t%i\t%i", sonarDistanceReading, eopdReading, red, green, blue);
		wait1Msec(50);
		clearDebugStream();

		checkButtons();
		//searchForBlocks();

		if (joystick.joy1_TopHat != -1)
		{
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
    else if ( abs(joystick.joy1_x2) > 20)
    {
      if (joystick.joy1_x2 > 20)
      {

      }
      else if (joystick.joy1_x2 < -20)
      {

      }
    }
    else if ( abs(joystick.joy1_y1) > 20)
    {
      if (joystick.joy1_x2 > 20)
      {

      }
      else if (joystick.joy1_x2 < -20)
      {

      }
    }
    else
    {

    }
	}
}