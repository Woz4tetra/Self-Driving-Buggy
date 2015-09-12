#pragma config(Hubs,  S1, HTMotor,  HTMotor,  none,     none)
#pragma config(Sensor, S2,     accelSensor,    sensorI2CCustom)
#pragma config(Motor,  mtr_S1_C1_1,     rightMotor,    tmotorTetrix, openLoop)
#pragma config(Motor,  mtr_S1_C1_2,     leftMotor,     tmotorTetrix, openLoop, reversed)
#pragma config(Motor,  mtr_S1_C2_1,     noMotor1,        tmotorTetrix, openLoop)
#pragma config(Motor,  mtr_S1_C2_2,     noMotor2,        tmotorTetrix, openLoop)

#include "C:\Program Files\Robomatter Inc\ROBOTC Development Environment\Sample Programs\NXT\3rd Party Sensor Drivers\drivers\hitechnic-accelerometer.h"

/* ----------
   Change log
   ----------

   4/18/13:				 Program created
   4/26/13: 3:48pm WARNING!!!
   								 !!! - This program may not work because the compass sensor isn't
   								 configured correctly

   								 It might be better to use the magnetic field sensor (less configurating)

   									Began to implement accelerometer plan:
   								 	1. get sensor reading HTACreadAllAxes()
   								 	2. Convert acceleration to distance
   								 		a. compound acceleration value into a velocity variable
   								 		b. convert velocity to distance by d = v * t
   								 	3. Interpret x and z values into angle and magnitude
   								 	4. If compass or gyro sensor doesn't equal angle, rotate
   								 	5. If magnitude of current x and z doesn't equal magntitude
   								 		 inputted x and z, then drive forward

   								 	Added:
   								 		void updateTimeCounter()

   								 		void accelToDistance(int &x, int &y, int &z)

   								 		int x_z_ToAngle(int x, int z)
   								 		int x_z_ToMag(int x, int z)

   								 		void rotate(int direction, int power, int time)
   								 		void rotate(int direction)

   								 		void driveForward(int direction, int power, int time)
   								 		void driveForward(int direction)

   								 		void goToPointFrom(int x_input, int z_input, int x_current, int z_current)

   								 		task main()

	 4/29/13: 3:49pm 		Deleted a lot of the previous program's methods:
	 											void updateTimeCounter()
   								 			void accelToDistance(int &x, int &y, int &z)
   								 			void goToPointFrom(int x_input, int z_input, int x_current, int z_current)
   								 		Added:
   								 			time1[T1] - a global clock in RobotC, counts in milliseconds
   								 					Now have to decide where to put the ClearTimer(T1); method
	 5/3/13: 4:30pm			Added:
	 											Acceleration Data collection (now can see that acceleration data is very sporadic
		 											writeDebugStream("\n\t%d", time1[T1]);
											   	writeDebugStream("\t%d", time1[T2]);
											   	writeDebugStream("\t%d", x_accel);
											   	writeDebugStream("\t%d", y_accel);
											   	writeDebugStream("\t%d", z_accel);

										  	Buffers for acceleration
										  		The accelerometer isn't perfect and can pick up extra noise
												    if (abs(x_accel) - abs(x_Calib) < accelerationBuffer)
												    	x_accel = 0;
												   	if (abs(y_accel) - abs(y_Calib) < accelerationBuffer)
												    	y_accel = 0;
												   	if (abs(z_accel) - abs(z_Calib) < accelerationBuffer)
												    	z_accel = 0;

											  A lot of static variables
											  	Reads out as a global variable on the debugger
											  	Not actually a global variable (a good thing)
											  	Can define them inside a method, initialize them once,
											  		and the program ignores the initialization for the
											  		rest of the program

	 										Changed:
 												Conversion changed from 9.8/200 to 9.806/200000

 											Removed:
 												All robot movement methods (for now)
 												Old code for buffers and calibration:
	 												x_accel /= 4; x_accel -= x_Calib;
											    y_accel /= 4; y_accel -= y_Calib;
											    z_accel /= 4; z_accel -= z_Calib;
*/

/*  --------------------------
 Adding to database methods
 Compiles the last 20 acceleration values to be sent to takeAverage()

 Precondition: value is either buffered, calibrated acceleration or velocity
 Postcondition: The array has value added to the end with all other values shifted down
                The first element of the array is deleted
 */

/*
  Arrays are global because RobotC doesn't take arrays as parameters as of May 2013
 */
int x_listAccel[20];
int y_listAccel[20];

int x_listVelocity[20];
int y_listVelocity[20];

/*  --------------------------
 Adding to database methods
 Compiles the last 20 acceleration values to be sent to takeAverage()

 Precondition: value is either buffered, calibrated acceleration or velocity
 Postcondition: The array has value added to the end with all other values shifted down
                The first element of the array is deleted
 */

int addToArray(int value, int selector)
{
		int index;
    if (selector == 0)
    {
        for (index = 0; index < 20 - 1; index++)
            x_listAccel[index] = x_listAccel[index + 1];

        x_listAccel[index + 1] = value;

        return selector;
    }
    else if (selector == 1)
    {
        for (index = 0; index < 20 - 1; index++)
            y_listAccel[index] = y_listAccel[index + 1];

        y_listAccel[index + 1] = value;

        return selector;
    }
    else if (selector == 2)
    {
        for (index = 0; index < 20 - 1; index++)
            x_listVelocity[index] = x_listVelocity[index + 1];

        x_listVelocity[index + 1] = value;

        return selector;
    }
    else if (selector == 3)
    {
        for (index = 0; index < 20 - 1; index++)
            y_listVelocity[index] = x_listVelocity[index + 1];

        x_listVelocity[index + 1] = value;

        return selector;
    }
}

/*  -------------------------
 The moving average method
 Takes the previous 20 acceleration values and averages them

 Precondition: list is an array of ints
 Postcondition: @return the average of all elements in list as an int
 */
int takeAverage(int selector)
{
    if (selector == 0)
    {
        int sum;

        for (int index = 0; index < 20; index++)
            sum += x_listAccel[index];

        return sum / 20;
    }
    else if (selector == 1)
    {
        int sum;

        for (int index = 0; index < 20; index++)
            sum += y_listAccel[index];

        return sum / 20;
    }
    else if (selector == 2)
    {
        int sum;

        for (int index = 0; index < 20; index++)
            sum += x_listVelocity[index];

        return sum / 20;
    }
    else if (selector == 3)
    {
        int sum;

        for (int index = 0; index < 20; index++)
            sum += y_listVelocity[index];

        return sum / 20;
    }
}

/*  ---------------------------
 Uses v0 + at = v equation

 in order to change velocity, accel needs to be the change in acceleration (accel0 - accel)
 initial acceleration is stored in task main (accel0)
 time1[T1] is in milliseconds

 Precondition: accel0 is the previous acceleration taken before accel or 0 the first run of the program
               velocity is the previous velocity to the last run of the method
 Postcondition: accel is passed to accel0
                accel is reevaluated in task main()
                calculated velocity is assigned to velocity0
                calculated velocity is returned based on CHANGE in acceleration
 */
int calculateVelocity(int &accel0, int &velocity0,  int accel)
{
    int velocity = velocity0 + (accel0 - accel) * 9.806/200 * time1[T1]/1000;

    velocity0 = velocity;
    accel0 = accel;

    return velocity;
}

/*  -----------
 time1[T1] is in milliseconds

 Precondition: velocity has been calculated by calculateVelocity()
 Postcondition: distance is calculated based on vt = d
 */
int calculateDistance(int velocity)
{
    return velocity * time1[T1]/1000;
}

/*  -----------------------------------------------------------
 Calibration set to acceleration at the beginning of program

 Precondition: accel0 is the acceleration value taken at the start of the program
 Postcondition: x, y, and z accel have all been calibrated
 */
void calibrateAcceleration(int x_accel, int y_accel, int z_accel, int x_accel0, int y_accel0, int z_accel0)
{
    static int x_initialAccel = x_accel0;
    static int y_initialAccel = y_accel0;
    static int z_initialAccel = z_accel0;

    x_accel -= x_initialAccel;
    y_accel -= y_initialAccel;
    z_accel -= z_initialAccel;
}

/*  ---------------
 Buffer set to 3
 if the absolute value of acceleration deviants from accelInitial by 3 or less, set acceleration to 0

 Precondition: accelInitial is the acceleration value taken at the start of the program
 Postcondition: accel has been buffered
 */
int bufferAccel(int &accel, int accelInitial);
{
    static int buffer = 3;

    if (abs(accel) - abs (accelInitial) < buffer) {
        accel = 0;
    }
}
/*  -----------------------------------------------
 An encompassing method for getting acceleration
 For Ben's OCD only

 Precondition: x, y, and z accel are int variables
 Postcondition: the three variables are assigned with values from the accelerometer
 */
void getAcceleration (int &x_accel, int &y_accel, int &z_accel)
{
    if (!HTACreadAllAxes (accelSensor, x_accel, y_accel, z_accel))
    {
        nxtDisplayTextLine (4, "ERROR!!");
        wait1Msec (2000);
        StopAllTasks();
    }
}

task main()
{
    int x_accel, x_accel0;
    int y_accel, y_accel0;
    int z_accel, z_accel0;

    int x_accelInitial;
    int y_accelInitial;
    int z_accelInitial;


    float x_velocity;
    float y_velocity;

    float x_velocity0;
    float y_velocity0;

    float x_distance;
    float y_distance;

    getAcceleration (x_accel, y_accel, z_accel);
    getAcceleration (x_accelInitial, y_accelInitial, z_accelInitial);

    calibrateAcceleration (x_accel, y_accel, z_accel, x_accelInitial, y_accelInitial, z_accelInitial);

    while (true)
    {
        ClearTimer (T1);

        getAcceleration (x_accel, y_accel, z_accel);

        calibrateAcceleration (x_accel, y_accel, z_accel, x_accel0, y_accel0, z_accel0);

        bufferAccel (x_accel);
        bufferAccel (y_accel);
        bufferAccel (z_accel);

        /*
         1. Add acceleration to array
         2. Take the moving average of the array
         3. Calculate velocity based on previous acceleration, acceleration, and previous velocity
         4. Add velocity to array
         5. Take the moving average of velocity
         6. Calculate distance based on velocity and time
         */
        //----------|---------------------------------------3-----------------------------------------|
        //----------|                                         |-------------------2-----------------|
        //----------|                                                      |------------1---------|
        x_velocity = calculateVelocity (x_accel0, x_velocity0, takeAverage (addToArray (x_accel, 0) ) );

        //----------|------------------------------6------------------------------|
        //----------|                  |--------------------5-------------------|
        //----------|                               |---------------4---------|
        x_distance = calculateDistance (takeAverage (addToArray (x_velocity, 2) ) );

        //=============================================================================================
        //=============================================================================================

        //----------|---------------------------------------3-----------------------------------------|
        //----------|                                         |-------------------2-----------------|
        //----------|                                                      |------------1---------|
        y_velocity = calculateVelocity (y_accel0, y_velocity0, takeAverage (addToArray (y_accel, 1) ) );

        //----------|------------------------------6------------------------------|
        //----------|                  |--------------------5-------------------|
        //----------|                               |---------------4---------|
        y_distance = calculateDistance (takeAverage (addToArray (y_velocity, 3) ) );

        //Feed distances to motors

        //----------------------------
		    //Acceleration Data collection
		    //----------------------------
		    writeDebugStream("\n\t%d", time1[T1]);
		   	writeDebugStream("\t%d", time1[T2]);
		   	writeDebugStream("\t%d", x_accel);
		   	writeDebugStream("\t%d", y_accel);
		   	writeDebugStream("\t%d", z_accel);
    }
}
