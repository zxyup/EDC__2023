# Servo Control Example
#
# This example shows how to use your OpenMV Cam to control servos.

import time
from pyb import Servo

s1 = Servo(1) # P7 上下控制
s2 = Servo(2) # P8 左右控制



#while(True):
    ##s1.angle(10)
    ##s2.angle(45)
    ##time.sleep(2)
    ##s1.angle(70)
    ##s2.angle(135)
    ##time.sleep(2)
    ##print(1)
    #s1.angle(-90)
    #time.sleep(1)
    #s1.angle(360)
    #time.sleep(1)


#s1.angle(0)
#s2.angle(0)

def toa(s,ang):
    step=1
    for i in range(ang-50,ang+step,step):
        s.pulse_width(i)
        time.sleep_ms(1)


#for i in range(1450,1500,5):
    #s1.pulse_width(i)
    #time.sleep_ms(5)
#for i in range(1350,1400,5):
    #s2.pulse_width(i)
    #time.sleep_ms(5)

toa(s1,1620)
toa(s2,1390)



#for i in range(1400,1710,10):
    ##s1.pulse_width(i)
    #s2.pulse_width(i)
    ##break
    #time.sleep_ms(100)


#while(True):



#死区
#while(True):
    #s2.pulse_width(1000)
    #for i in range(1000,1400,5):
        #s2.pulse_width(i)
        #time.sleep_ms(5)
    #time.sleep(1)
    #s2.pulse_width(1700)
    #for i in range(1700,1400,-5):
        #s2.pulse_width(i)
        #time.sleep_ms(5)
    #time.sleep(1)



##死区
#while(True):
    #s2.pulse_width(1000)
    #time.sleep(1)
    #s2.pulse_width(1400)
    #time.sleep(1)
    #s2.pulse_width(1700)
    #time.sleep(1)
    #s2.pulse_width(1400)
    #time.sleep(1)
