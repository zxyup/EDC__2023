# Servo Control Example
#
# This example shows how to use your OpenMV Cam to control servos.

import time
from pyb import Servo

y = Servo(1) # P7 上下控制
x = Servo(2) # P8 左右控制



#while(True):
    ##y.angle(10)
    ##x.angle(45)
    ##time.sleep(2)
    ##y.angle(70)
    ##x.angle(135)
    ##time.sleep(2)
    ##print(1)
    #y.angle(-90)
    #time.sleep(1)
    #y.angle(360)
    #time.sleep(1)


#y.angle(0)
#x.angle(0)

def toa(s,ang):
    step=1
    for i in range(ang-50,ang+step,step):
        s.pulse_width(i)
        time.sleep_ms(1)

def tov(xx,yy):
    toa(y,yy)
    toa(x,xx)
    #toa(y,yy)





(1390,1620)

#toa(y,1620)
#toa(x,1390)

tov(1680,1620)




#while(True):



#死区
#while(True):
    #x.pulse_width(1000)
    #for i in range(1000,1400,5):
        #x.pulse_width(i)
        #time.sleep_ms(5)
    #time.sleep(1)
    #x.pulse_width(1700)
    #for i in range(1700,1400,-5):
        #x.pulse_width(i)
        #time.sleep_ms(5)
    #time.sleep(1)


#for i in range(1450,1500,5):
    #y.pulse_width(i)
    #time.sleep_ms(5)
#for i in range(1350,1400,5):
    #x.pulse_width(i)
    #time.sleep_ms(5)

##死区
#while(True):
    #x.pulse_width(1000)
    #time.sleep(1)
    #x.pulse_width(1400)
    #time.sleep(1)
    #x.pulse_width(1700)
    #time.sleep(1)
    #x.pulse_width(1400)
    #time.sleep(1)
