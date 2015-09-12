
//--------------------------------------------------------------------
//                       Global variables
//--------------------------------------------------------------------

#define ARRAYSIZE(a) (sizeof(a)/sizeof(a[0]))

// goalPosition
float goalX, goalY, goalAngle, endAngle = -1;
float previousGoalX = 0, previousGoalY = 0;

// currentPosition
float currentX, currentY, currentAngle;

bool doesRobotStrafe = true;

// Encoder variables
int encoderEntachTrackballParallel; // 0
int encoderEntachTrackballOrthogonal; // 2
int encoderEntachParallel; // 1

float encoderDelta[3];
float encoderSpeed[3];

// in encoder counts:
int trackballParallel1, trackballParallel2;
int trackballOrthogonal1, trackballOrthogonal2;
int parallel1, parallel2;

// in cm:
float etpd, etod, epd;

float encoderToCM; // in cm
float rtp, rto, rp; // in cm
float maximumRobotSpeed; // in cm / sec

// Acceleration variables
bool motorsStopped = true;
int  motorAccel = 0;

// Timer variables
long timer[4];

// goToGoalPosition Variables
bool goToGoalPositionIsRunning = false;

// Obstacle sensor readings
float obstacleReadingLeft;
float obstacleReadingRight;

//--------------------------------------------------------------------
//                       Method initializations
//--------------------------------------------------------------------

    //---------------------------------------------------------------------------------
    // Implemented in Robot_Common.h ("Robot" should be replaced with your robot name)
    //---------------------------------------------------------------------------------
    void resetEntachEncoders();
    task encoderEntachReadout();

    task updateObstacleSensors();

    void initializeEntachVariables();

    void stopMotors();
    void driveForward(int inputSpeed);
    void driveBackward(int inputSpeed);
    void driveLeft(int inputSpeed);
    void driveRight(int inputSpeed);
    void rotateLeft(int inputSpeed);
    void rotateRight(int inputSpeed);
    void driveWithStrafingVelocity (float angleRadians, int maxMotorSpeed);

    //---------------------------------------------------------------------------------
    //                  Implemented in Entach_Common.h (this file)
    //---------------------------------------------------------------------------------
    task accelerationSetter();

    float correctAngle (float angle);

    void initializeAxes(float x, float y, float angleInRadians);
    float getRelativeRadius (float inputX, float inputY, float currentX, float currentY);
    float getGoalAngle (float inputX, float inputY);

    void goToAngle(float inputGoalAngle);
    void goToDistance(float inputGoalX, float inputGoalY, float inputCurrentX, float inputCurrentY);
    void strafeToGoalPosition();

    task updateEncoderSpeeds();

    task updatePosition();

    void startGoToGoalPosition();
    void stopGoToGoalPosition();
    bool hasGoalPositionBeenReached();
    float getDriftConstant();
    bool detectDrift();
    bool detectObstacle();
    void findOpenPath();

    void goToPoint(float inputX, float inputY);
    void goToPoint(float inputX, float inputY, float inputEndAngle);
    task goToGoalPosition();

//--------------------------------------------------------------------
//                         Motor drive methods
//--------------------------------------------------------------------

/*
If the driving motors are activated, motorSpeed will slowly accelerate from 20 to 100
If the driving motors are deactivated, motorSpeed will quickly deccelerate from 100 to 0

This is an alternative to speed switching (start slow for inching towards something,
speeding up for traversing longer distances
*/

task accelerationSetter()
{
    while (true)
    {
        if(motorsStopped == true)
        {
            while (motorsStopped == true)
            {
                motorAccel = 0;
            }
        }

        else
        {
            motorAccel = 40;

            while(motorsStopped == false)
            {
                motorAccel++;

                if (motorAccel > 100)
                motorAccel = 100;

                wait1Msec(40);
            }
        }
    }
}

//--------------------------------------------------------------------
//                          Helper angle methods
//--------------------------------------------------------------------

float correctAngle (float angle)
{
    if (angle < 0)
    {
        angle += 2 * PI;
    }
    if (angle >= 2 * PI)
    {
        angle -= 2 * PI;
    }
    return angle;
}

float correctAngle (float angle, float lowerBound, float upperBound)
{
    if (angle < lowerBound)
    {
        angle += 2 * PI;
    }
    if (angle >= upperBound)
    {
        angle -= 2 * PI;
    }
    return angle;
}

//--------------------------------------------------------------------
//						Angle and Distance calculation methods
//--------------------------------------------------------------------

void initializeAxes(float x, float y, float angleInRadians)
{
    currentX = x;
    currentY = y;
    currentAngle = correctAngle(angleInRadians);
}

float getRelativeRadius (float inputX, float inputY, float currentX, float currentY)
{
    // distance formula
		float distance = sqrt( pow(inputY - currentY, 2) + pow(inputX - currentX, 2));

		if (!(goalX - currentX > 0 && goalY - currentY > 0)) {
			distance *= -1;
		}

    return distance;
}

float getGoalAngle (float inputX, float inputY)
{
    // arctan2, returns in radians
    /* atan2() was chosen over atan() because atan2 has the ability to determine what quadrant
     the angle based on x and y should be in. atan cannot discern between an input of -x / +y
     and +x / -y which, in reality, are in completely different quadrants. atan2 is computed
     using a piecewise function which previous versions of this program were trying to achieve
     ( http://en.wikipedia.org/wiki/Atan2#Definition_and_computation ). Now goalAngle has the same
     domain of 0...2 * pi as currentAngle!
     */
    float angle = atan2 ( inputY - currentY, inputX - currentX );

    if ( angle != angle ) // if goalAngle = +/-nan
    	return currentAngle;
   	else
    {
        /* "if (goalAngle < 0)" is here because currentAngle's range is 0...2 * pi radians
         while atan2's range is -pi...pi. However, we can't just add pi to every result of arctan2
         because that would cause arctan2(0) to equal pi which is incorrect. For these two reasons,
         pi is only added when goalAngle < 0 is true.
         */
        if (angle < 0)
            angle += 2 * PI;

        return angle;
    }
}

//--------------------------------------------------------------------
//						Helper "goTo" methods
//--------------------------------------------------------------------

// if goal heading does not equal current heading, turn left or right
void goToAngle(float inputGoalAngle)
{
    float turnAngle = correctAngle(inputGoalAngle - currentAngle, -PI, PI);

    while (abs(turnAngle) > 0.05)
    {
        if (turnAngle < 0.05) {
            rotateRight(20);
        }
        else if (turnAngle > 0.05) {
            rotateLeft(20);
        }
        turnAngle = correctAngle(inputGoalAngle - currentAngle, -PI, PI);
    }

  	stopMotors();
  	wait1Msec(50);
}

void goToDistance(float inputGoalX, float inputGoalY, float inputCurrentX, float inputCurrentY)
{
    float currentRadius = 0;
    float goalRadius = getRelativeRadius(inputGoalX, inputGoalY, inputCurrentX, inputCurrentY);

    if (goalRadius == 0) {
        return;
    }

    while ( abs( currentRadius - goalRadius ) >= 0.05 ) //Error buffer of 0.05 cm (so that the robot doesn't search forever)
    {
        currentRadius = getRelativeRadius(currentX, currentY, inputCurrentX, inputCurrentY);

        if (currentRadius < goalRadius) {
            driveForward(25);
        }
        else {
            driveBackward(25);
        }
    }
    stopMotors();
    wait1Msec(50);
}

void strafeToGoalPosition()
{
    while (abs(currentX - goalX) >= 0.05 && abs(currentY - goalY) >= 0.05)
    {
        //Strafe to point
        driveWithStrafingVelocity (goalAngle, 50);
    }
    stopMotors();
    wait1Msec(50);
}

//--------------------------------------------------------------------
//						Encoder speed updater
//--------------------------------------------------------------------

task millisecondTimer()
{
    while (true)
    {
        for (int index = 0; index < ARRAYSIZE(timer); index++) {
            timer[index]++;
        }
        wait1Msec(1);
    }
}

task updateEncoderSpeeds()
{
    StartTask(millisecondTimer);

    while (true)
    {
        for (int index = 0; index < ARRAYSIZE(encoderSpeed); index++)
        {
            if (timer[index] != 0)
            {
                encoderSpeed[index] = (float)encoderDelta[index] / (float)timer[index]; // cm / sec
                timer[index] = 0;
            }
        }
    }
}

//--------------------------------------------------------------------
//						Current position updaters
//--------------------------------------------------------------------

task updatePosition()
{
    float changeInParallelMovement, changeInOrthogonalMovement, changeInAngularMovement;

    trackballParallel1 = encoderEntachTrackballParallel;
    trackballOrthogonal1 = encoderEntachTrackballOrthogonal;
    parallel1 = encoderEntachParallel;

    while (true)
    {
        wait1Msec(5);

        trackballParallel2 = encoderEntachTrackballParallel;
        trackballOrthogonal2 = encoderEntachTrackballOrthogonal;
        parallel2 = encoderEntachParallel;

        etpd = (trackballParallel2 - trackballParallel1) * encoderToCM; // Encoder Trackball Parallel Delta
        etod = (trackballOrthogonal2 - trackballOrthogonal1) * encoderToCM; // Encoder Trackball Orthogonal Delta
        epd = (parallel2 - parallel1) * encoderToCM; // Encoder Parallel Delta

        changeInParallelMovement = (epd * rtp + etpd * rp) / (rp + rtp);
        changeInOrthogonalMovement = (epd * rto + etod * (rp + rtp) - etpd * rto) / (rp + rtp);
        changeInAngularMovement = -(epd - etpd)/(rp + rtp);

        currentAngle += changeInAngularMovement; currentAngle = correctAngle(currentAngle);
        currentY +=  changeInOrthogonalMovement * cos(currentAngle) + changeInParallelMovement * sin(currentAngle);
        currentX += -changeInOrthogonalMovement * sin(currentAngle) + changeInParallelMovement * cos(currentAngle);

        if (etpd != 0 || etod != 0 || epd != 0)
        {
            //writeDebugStreamLine("%f, %f, %f", changeInParallelMovement, changeInOrthogonalMovement, changeInAngularMovement);
            writeDebugStreamLine("x: %f, y: %f, a: %f", currentX, currentY, currentAngle);
            //writeDebugStreamLine("%i\t%i\t%i", encoderEntachTrackballParallel, encoderEntachTrackballOrthogonal, encoderEntachParallel);
            //writeDebugStreamLine("tp: %f, to: %f, p: %f", etpd, etod, epd);
        }

        trackballParallel1 = trackballParallel2; // not encoderEntachTrackballParallel
        trackballOrthogonal1 = trackballOrthogonal2;
        parallel1 = parallel2;
    }
}


//--------------------------------------------------------------------
//                    goToGoalPosition() helper methods
//--------------------------------------------------------------------

void startGoToGoalPosition()
{
    goToGoalPositionIsRunning = true;
    StartTask(goToGoalPosition);
}

void stopGoToGoalPosition()
{
    goToGoalPositionIsRunning = false;
    StopTask(goToGoalPosition);
}

bool hasGoalPositionBeenReached()
{//0.05, 0.05, 0.005
    if (abs(goalX - currentX) < 0.5 && abs(goalY - currentY) < 0.5 && abs(goalAngle - currentAngle) < 0.05 ) {
        return true;
    }
    else {
        return false;
    }
}

float y_getDriftConstant()
{
    float slope = (goalY - previousGoalY) / (goalX - previousGoalX);
    
    return slope * (currentX - goalX) - (currentY - goalY);
}

float x_getDriftConstant()
{
    float slope = (goalX - previousGoalX) / (goalY - previousGoalY);
    
    return slope * (currentY - goalY) - (currentX - goalX);
}

float getDriftConstant() {
    return getRelativeRadius(x_getDriftConstant(), y_getDriftConstant(), 0, 0);
}

bool detectDrift()
{
    if (abs(getDriftConstant()) > 1 || abs(goalAngle - currentAngle) > 0.05) {
        return true;
    }
    else {
        return false;
    }
}

bool detectObstacle()
{
    static float previousEncoderSpeed[3];
    bool obstacleDetected = false;

    for (int index = 0; index < ARRAYSIZE(previousEncoderSpeed); index++)
    {
        if (encoderSpeed[index] - previousEncoderSpeed[index] < -4) { //-4 cm / sec
            // If the speed of any encoder drops by 4 cm / sec, an obstacle has been hit
            obstacleDetected = true;
        }
    }
    if (obstacleReadingLeft < 5 && obstacleReadingRight < 5) {
        // If either obstacle sensor reads less than 5 cm, an obstacle has been hit
        obstacleDetected = true;
    }

    for (int index = 0; index < ARRAYSIZE(previousEncoderSpeed); index++) {
        previousEncoderSpeed[index] = encoderSpeed[index];
    }

    return obstacleDetected;
}

void findOpenPath()
{
    float initialCurrentAngle = currentAngle;
    timer[3] = 0;

    while (timer[3] / 1000 < 5) // search for 5 seconds maximum
    {
        if (currentAngle - initialCurrentAngle < 2.96705972839036) { // 2.96705972839036 radians = 170 degrees
            rotateLeft(30);
        }
        else if (currentAngle - initialCurrentAngle < 6.10865238198015) { // 6.10865238198015 radians = 350 degrees
            rotateRight(30);
        }

        if (obstacleReadingLeft > 50 && obstacleReadingRight > 50) { // 50 cm
            return;
        }
    }
}

//--------------------------------------------------------------------
//                        goToGoalPosition()
//--------------------------------------------------------------------

void goToPoint(float inputX, float inputY)
{
    goalX = inputX;
    goalY = inputY;

    goalAngle = getGoalAngle(inputX, inputY);

    writeDebugStreamLine("goalAngle: %f", goalAngle);

    while (hasGoalPositionBeenReached() == false)
    {
        if (goToGoalPositionIsRunning == false) {
        		writeDebugStreamLine("\ngoToGoalPosition() started");
            startGoToGoalPosition();
        }
				/*
        if (detectObstacle() == true)
        {
            stopGoToGoalPosition();

            goToDistance(-15);

            findOpenPath();

            goToDistance(65);
        }*/

        if (detectDrift() == true)
        {
            stopGoToGoalPosition();
            goToAngle(goalAngle);
            
            while (abs(getDriftConstant()) > 1)
            {
                if (getDriftConstant() < -1)
                {
                    driveRight(30);
                }
                else if (getDriftConstant() > 1)
                {
                    driveLeft(30);
                }
            }
            
            stopMotors();
            wait1Msec(10);
        }
    }
}

void goToPoint(float inputX, float inputY, float inputEndAngle)
{
    endAngle = inputEndAngle;

    goToPoint(inputX, inputY);
    goToAngle(endAngle);
    endAngle = -1;
}

task goToGoalPosition()
{
    if (currentAngle == endAngle) {
        strafeToGoalPosition();
    }
    else
    {
        goToAngle(goalAngle);

        while (hasGoalPositionBeenReached() == false) {
        		goToDistance(goalX, goalY, currentX, currentY);
        }

        if (endAngle != -1) {
        		goToAngle(endAngle);
      	}

      	previousGoalX = goalX;
	    	previousGoalY = goalY;
    }
}
