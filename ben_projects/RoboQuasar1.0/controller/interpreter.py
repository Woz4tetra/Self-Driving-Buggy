# interprets sensor data from board/data.py to x, y, theta (current position)

# pitch=atan2(accx,sqrt(accy^2+accz^2))
# roll=atan2(accy,sqrt(accx^2+accz^2))
# Heading (or yaw) =atan2( (-ymag*cos(Roll) + zmag*sin(Roll) ) , (xmag*cos(Pitch) + ymag*sin(Pitch)*sin(Roll)+ zmag*sin(Pitch)*cos(Roll)) ) 
import math

def get_position(imu, gps, encoder):
    

