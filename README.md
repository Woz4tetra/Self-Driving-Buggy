# Self-Driving Buggy
This project aims to develop autonomous localization and navigation in a minimally-invasive retrofit package for retired buggy vehicles. Given a retired frame and shell buggy from a Sweepstakes (aka. Buggy) organization, the buggy would be able to navigate and complete the given course under varying conditions. A long term goal of the project would be to allow the self-driving buggy to race human drivers on Race Day in April.

### Version
- 10/3/2015

## Dependencies
* [OpenCV3](http://opencv.org) - Open source read-time computer vision algorithms
* [PlatformIO](http://platformio.org) - "PlatformIO is a cross-platform code builder and the missing library manager"
* [PySerial](https://github.com/pyserial/pyserial) - "This module encapsulates the access for the serial port."
* [Arduino-serial-messaging](https://github.com/jeroendoggen/Arduino-serial-messaging) - "Library to exchange short messages (sensordata, commands) between an Arduino and a software application running on a PC. (Linux, embedded Linux, Windows, OS X) (clients currently under development)"
* [i2cdevlib](http://www.i2cdevlib.com/) - An Arduino I2C interface library

## Installation
### Install OpenCV
##### Mac
1. Install Homebrew:
```
$ ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
2. Install OpenCV3 and dependencies
```
$ brew update
$ brew tap homebrew/science
$ brew install opencv3
$ brew install matplotlib
```
3. Install PySerial
```
pip install pyserial
```
4. Install PlatformIO
```
pip install platformio
```

## Style Guide
- python modules (python directories included), functions, and variables use underscore (ex. buggy_info, video_maker)
- c++ files use capitalized camel case (ex. SerialComm.cpp, AccelStepper.cpp, NewPing.cpp)
- Directories follow c++ convention or normally spaced words (if able)
- Top level project directories follow whatever the owner prefers (ex. ben_projects, chrisProjects, NatProjects)
- Object oriented properties, methods, and names use camel case
- put a doc string with the following info at the top of a main file and have it display when the program runs. Example doc string:
```
Written by Ben Warwick

Self-Driving Buggy Rev. 6 (__main__.py) for Self-Driving Buggy Project
Version 9/15/2015
=========

This program controls the self-driving buggy. It manages computer vision,
microcontroller control and data collection, PID feedback, encoder to x, y
algorithms, path finding, GPS algorithms, and IMU algorithms. Each of these is
implemented in its own file.

Usage
-----
python __main__.py

– or – (in folder directory):
python Self-Driving Buggy Rev. 6

Dependencies
------------
PySerial - https://github.com/pyserial/pyserial
OpenCV 3.0.0 (and its dependencies) - http://opencv.org

Keys
----
    q, ESC - exit
    SPACE - play/pause video
    o - toggle show original video feed
    left - read previous frame
    right - read next frame
    s - save frame as image (in camera/Images/ directory)
    v - start/stop create video (saved in camera/Videos/ directory)
    h - toggle enable draw (hide/show video feed)
```

```python
def run():
    pass

if __name__ == '__main__':
    print __doc__
    run()
```
- use python's commenting format for each function. Example function doc string:
```python
def initVideoWriter(self, fps=30, name="", includeTimestamp=True,
                        codec='mp4v', format='m4v'):
    '''
    Initialize the Capture's video writer.

    :param fps: The playback FPS of the video. This number can be finicky as
            the capture's current FPS may not match the video's output FPS.
            This is because video playback takes less computation than
            analyzing the video in this setting.
    :param name: The name of the video. If "", a time stamp will
            automatically be inserted
    :param includeTimestamp: An optional parameter specifying whether the
            time should be included. True by default
    :param codec: The output video codec. mp4v is recommended
    :return: None
    '''
```





