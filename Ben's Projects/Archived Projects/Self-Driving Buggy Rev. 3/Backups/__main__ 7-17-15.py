import sys
# import time

import arduino
import buggyinfo
import draw
import kalman

def run():
    motorSpeed = 40
    motorForward = False
    
#    motor = arduino.DCMotor(1)
#    IMU = arduino.IMU()
    # button1 = Arduino.Button(0)

    posX = buggyinfo.position(0)
    posY = buggyinfo.position(0)
    posZ = buggyinfo.position(0)
    
    drawer = draw.Drawer(200, 200, 700, 700, (20, 20), (70, 80))
    
    while drawer.done is False:
#        if motorForward == True:
#            motor.driveForward(motorSpeed)
#        else:
#            motor.driveBackward(motorSpeed)

#        motorSpeed += 5
#        if motorSpeed > 255:
#            motorSpeed = 40
#            motorForward = not motorForward
#        data = IMU.getIMU()
        data = drawer.getAccel()
        accel = accel = kalman.smooth(data[0:3])
        yaw, pitch, roll = data[3:6]
        dt = data[6]

        posX.update(accel[0], dt)
        posY.update(accel[1], dt)
        posZ.update(accel[2], dt)

        print (posX, posY, posZ), (yaw, pitch, roll), accel
        
        drawer.loop()
        drawer.drawParticle(int(posX), int(posY))
        drawer.update()
    
    drawer.deinit()
    arduino.arduino.stop()


if __name__ == '__main__':
    arguments = sys.argv
    if "help" in arguments or "h" in arguments:
        print NotImplementedError
    if "upload" in arguments:
        arduino.initBoard(upload=True)
    elif "load" in arguments:
        arduino.initBoard(uploadOnly=True)
        quit()
    else:
        arduino.initBoard(disabled=True)

    run()
