#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()
# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096


pwm.set_pwm_freq(50)

print('Moving servo on channel 0, press Ctrl-C to quit...')

pwm.set_pwm(5,0,325)  # 底座舵机   290     370左
pwm.set_pwm(4,0,250)  # 倾斜舵机   260     350  下  

# while(1):
#     set_servo_angle(12,60)
#     time.sleep(2)
#     set_servo_angle(12,90)
#     time.sleep(2)
#     set_servo_angle(12,130)
#     time.sleep(2)
#     set_servo_angle(12,90)
#     time.sleep(2)

# pwm.set_pwm(4, 0, 300)
# time.sleep(1)
# pwm.set_pwm(5, 0, 300)
# time.sleep(1)
