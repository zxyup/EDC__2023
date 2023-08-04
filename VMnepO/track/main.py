#from find import fb
#from mpid import *
#from motor import *
import sensor, image, time
from pyb import Servo


y = Servo(1) # P7 上下控制
x = Servo(2) # P8 左右控制

xx=1250
yy=1580

def ctrl(xx,yy):
    y.pulse_width(yy)
    x.pulse_width(xx)

ctrl(xx,yy)

def fb(threshold,imgg):
    blobs = imgg.find_blobs([threshold],x_stride=1,y_stride=1)
    if blobs:
        b = blobs[0]
        cx = b.cx()
        cy = b.cy()
        return cx, cy
    return None, None

class PID:
    def __init__(self, kp, ki, kd):
        self.__version__ = "0.0.1"
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.err = 0
        self.sum_err = 0
        self.last_err = 0
    #--------PID送入----------------------
    def setErr(self, err):
        self.err = err
        self.sum_err += err
    #--------PID送出----------------------
    def output(self,err):
        self.err = err
        self.sum_err += err
        out = self.kp * self.err
        out += self.ki * self.sum_err
        out += self.kd * (self.err-self.last_err)
        self.last_err = self.err
        return out


clock = time.clock()

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_gain(1)
sensor.set_auto_exposure(False, exposure_us=1400)
sensor.set_auto_whitebal(0)
sensor.skip_frames(20)

red_threshold = (55, 90, -4, 94, -4, 107)  # 红色激光笔的颜色阈值
red_threshold =(55, 98, 5, 127, -25, 104)
#red_threshold =(100, 0, 127, 36, -21, 15)
green_threshold = (9, 86, 10, 71, -2, 66)    # 绿色十字的颜色阈值
green_threshold=(75, 100, -114, 14, -94, 107)
green_threshold=(82, 100, -54, 7, -47, 65)
green_threshold=(82, 100, -89, -6, -40, 65)

sf=1


#px=PID(0.1,0,0.005)
#py=PID(0.04,0,0.005)

px=PID(0.8,0.01,0.43)
py=PID(0.8,0.01,0.53)



def move(ct,cn):
    cnx,cny=cn
    ctx,cty=ct
    global xx,yy
    xx+=px.output(cnx-ctx)
    yy-=py.output(cny-cty)
    print('x=',xx,'   y=',yy)
    if xx<950:
        xx=950
    if xx>1450:
        xx=1450
    if yy<1460:
        yy=1460
    if yy>1800:
        yy=1800
    y.pulse_width(int(yy))
    x.pulse_width(int(xx))



while True:
    clock.tick()
    img = sensor.snapshot().lens_corr(strength=1.8, zoom=1.0)


    tf=1

    # 检测红色激光笔的位置
    ct = fb(red_threshold,img)

    cx, cy = ct
    if cx and cy:
        #print(ct)
        if sf:
            img.draw_cross(cx, cy, color=(0,255, 0))
    else:
       tf=0

    # 检测绿色激光笔的位置
    cn = fb(green_threshold,img)

    cx, cy = cn
    if cx and cy:
        print('cn=',cn)
        if sf:
            img.draw_cross(cx, cy, color=(255, 0,0))
    else:
       tf=0

    if tf:
        move(ct,cn)

    # 显示图像
    #img.draw_cross(80, 60, color=(255, 0, 0))  # 中心位置绘制红色十字
    #img = img.to_rgb565()
    #print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected
