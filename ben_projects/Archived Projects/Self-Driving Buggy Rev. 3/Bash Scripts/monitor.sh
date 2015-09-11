#!/bin/sh
cd ..
python __main__.py load
platformio serialports monitor --port /dev/cu.usbmodem1411 --baud 38400