from pyb import *
from objects import Motor

def pwm_test():
    pwm_3 = Pin('X3')
    timer_3 = Timer(2, freq=1000)

    pwm_channel = timer_3.channel(3, Timer.PWM, pin=pwm_3)
    
    enable_2 = Pin('X2', Pin.OUT_PP)
    enable_2.value(1)
    
    while True:
        print("pwm: 100")
        pwm_channel.pulse_width_percent(100)
        pyb.delay(2000)
        
        print("pwm: 50")
        pwm_channel.pulse_width_percent(50)
        pyb.delay(2000)
        
        print("pwm: 0")
        pwm_channel.pulse_width_percent(0)
        pyb.delay(2000)

def analog_test():
    enable_2 = Pin('X2', Pin.OUT_PP)
    enable_2.value(1)
    enable_3 = Pin('X3', Pin.ANALOG)
    while True:
        enable_2.value(int(not enable_2.value()))
        print("analog: 255, ", enable_2.value())
        enable_3.value(255)
        pyb.delay(2000)
        
        enable_2.value(int(not enable_2.value()))
        print("analog: 127, ", enable_2.value())
        enable_3.value(127)
        pyb.delay(2000)
        
        enable_2.value(int(not enable_2.value()))
        print("analog: 0, ", enable_2.value())
        enable_3.value(0)
        pyb.delay(2000)

def scale_test():
    enable_2 = Pin('X2', Pin.OUT_PP)
    enable_2.value(1)
    print("enable pin:", enable_2.value())
    analog_3 = Pin('X3', Pin.ANALOG)
    while True:
        for speed in range(256):
            analog_3.value(speed)
            pyb.delay(250)
            print(analog_3.value(), speed)
        
        for speed in range(255, -1, -1):
            analog_3.value(speed)
            pyb.delay(500)
            print(analog_3.value())

def lib_test():
    motor_a = Motor(0, 'X2', 'X3')
    while True:
        # for value in range(-100, 100, 1):
        #     motor_a.speed(value)
        #     delay(50)
        #     print(motor_a.speed())
       motor_a.speed(100)
       print(motor_a.speed())
       delay(2000)
       motor_a.speed(-100)
       print(motor_a.speed())
       delay(2000)

lib_test()
