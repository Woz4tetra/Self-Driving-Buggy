#!/bin/sh
cd ..
cd Calibration
platformio run --target upload
platformio serialports monitor --port /dev/cu.usbmodem1411 --baud 38400