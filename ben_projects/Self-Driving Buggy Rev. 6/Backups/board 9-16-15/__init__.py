'''
This module contains all arduino communication methods and classes.

Example usage:
arduino.initBoard()
stepper = arduino.Stepper(1)
IMU = arduino.IMU()

while True:
    accel, gyro, dt = IMU.getIMU()
    stepper.moveTo(100)

For more details on...
    how Stepper and IMU work, type help(arduino.Device).
    what initBoard does, type help(arduino.initBoard) and help(arduino.Board)

Dependencies:
- platformio: http://platformio.org/#!/
- pyserial: https://pypi.python.org/pypi/pyserial
'''

from devices import _initBoard

def initBoard(address=None, baud=38400, disabled=False, upload=True,
              sketchDir=''):
    '''
    All instances of Peripherals reference one instance of arduino. Call
    initBoard once in your main code.

    :param address: The USB serial address reference. example on mac:
            dev/cu.usbmodem1411
    :param baud: This rate (int, long) must match the number contained in the
            arduino sketch (specified by sketchDir) ex. Serial.begin(38400);
    :param disabled: If you want to run your code without commenting out
            all objects that use arduino, set this to True
    :param disabled: If you want to upload the arduino sketch before running
            your code.
    :param sketchDir: The directory of the arduino sketch to upload starting
            from the project directory
    :return: None
    '''
    _initBoard(address, baud, disabled, upload, sketchDir)
