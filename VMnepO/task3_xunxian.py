#****************包声明***********************
#import numpy as np
#import matplotlib.pyplot as plt
import sensor,image,time
from pyb import Servo
#=============变量声明======================
#------------PID变量-----------------------
class PIDCtrl:
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
    def output(self):
        out = self.kp * self.err
        out += self.ki * self.sum_err
        out += self.kd * (self.err-self.last_err)
        self.last_err = self.err
        return out

PID_Laser_2_Point=PIDCtrl(1,0,0)

#------------交互变量-----------------------
reset_botton=0
task1_botton=0
task2_botton=0
task3_botton=0
#--------任务1/2：铅笔云台参数---------------
pencil_center=[0,0]  #使得铅笔指向中心的舵机角度
pencil_lu=[0,0]      #left / up
pencil_ru=[0,0]
pencil_rd=[0,0]
pencil_ld=[0,0]
#--------任务3/4：激光与框参数---------------
laser_position=[0,0]                   #当前激光的位置
rect_position=[[0,0],[0,0],[0,0],[0,0]]#识别到的框的位置

#--------任务3/4：舵机死区参数---------------

Servo_X_Death_Pixcel=5 #准确到达目标的最优步进距离
Servo_Y_Death_Pixcel=5
Servo_X_Step_Pixcel=5  #不跑出黑框的最优步进距离
Servo_Y_Step_Pixcel=5
Servo_X_Step_time=1000  #精准跑一个step长度所需的最短时间
Servo_Y_Step_time=1000
Servo_X_Now_Ang=0
Servo_Y_Now_Ang=0
#============函数声明=======================
#------------按钮初始化---------------------
def Button_Init(botton):
    reset_botton=botton[0]
    task1_botton=botton[1]
    task2_botton=botton[2]
    task3_botton=botton[3]
#------------获取按钮值---------------------
def Button_Get():
    reset_botton=0
    task1_botton=0
    task2_botton=0
    task3_botton=0
#-------------舵机初始化--------------------
def Servo_Init():
     global s1
     global s2
     s1 = Servo(1)#P7
     s2 = Servo(2)#P8
#--------------云台移动---------------------
def Servo_Excute(angle,times):
    global Servo_X_Now_Ang
    global Servo_Y_Now_Ang
    Servo_X_Now_Ang=Servo_X_Now_Ang+angle[0]
    Servo_Y_Now_Ang=Servo_Y_Now_Ang+angle[1]
    s1.angle(Servo_Y_Now_Ang,times[1])
    s2.angle(Servo_X_Now_Ang,times[0])
    print("X_d=",angle[0],"Y_d=",angle[1],"X_o=",Servo_X_Now_Ang,"Y_o=",Servo_Y_Now_Ang)
    #time.sleep_ms(times[0])


#------------Rect get--------------------
task3_rect_thresholds=20                       #长宽大于20像素的框，才被视为有效的黑框
task3_rect_max_thres=10000                     #长度小于10000像素的框，才被视为有效的黑框
corners=[[0,0],[0,0],[0,0],[0,0]]
def Find_Rect():
    find_rect_count=0
    global corners
    corners[0][0]=0
    corners[0][1]=0
    corners[1][0]=0
    corners[1][1]=0
    corners[2][0]=0
    corners[2][1]=0
    corners[3][0]=0
    corners[3][1]=0

    while(find_rect_count<=9):
        img = sensor.snapshot()
        for r in img.find_rects(threshold = task3_rect_max_thres):
            if r.w() > task3_rect_thresholds and r.h() > task3_rect_thresholds:
                corner=r.corners()
                corners[0][0]+=corner[0][0]
                corners[0][1]+=corner[0][1]
                corners[1][0]+=corner[1][0]
                corners[1][1]+=corner[1][1]
                corners[2][0]+=corner[2][0]
                corners[2][1]+=corner[2][1]
                corners[3][0]+=corner[3][0]
                corners[3][1]+=corner[3][1]
                find_rect_count=find_rect_count+1
    corners[0][0]=int(corners[0][0]/10)
    corners[0][1]=int(corners[0][1]/10)
    corners[1][0]=int(corners[1][0]/10)
    corners[1][1]=int(corners[1][1]/10)
    corners[2][0]=int(corners[2][0]/10)
    corners[2][1]=int(corners[2][1]/10)
    corners[3][0]=int(corners[3][0]/10)
    corners[3][1]=int(corners[3][1]/10)
#------------激光位置获取-------------------
laser_roi=[0,0,128,160]
laser_roi_wh=30
#laser_thresholds=[(61, 78, 19, 50, -39, 68)]   #激光LAB色块值
laser_thresholds=[(100, 0, 127, 36, -21, 15)]
is_vision=0
def Laser_Update(img):
    global is_vision
    is_vision=0
    for laser_blobs in img.find_blobs(laser_thresholds,pixels_threshold=1, area_threshold=1, merge=True,invert = 0,roi=laser_roi):
        is_vision=1
        laser_roi[0]=int(laser_blobs.x()-int(laser_roi_wh/2))
        laser_roi[1]=int(laser_blobs.y()-int(laser_roi_wh/2))
        laser_roi[2]=laser_roi_wh
        laser_roi[3]=laser_roi_wh
        laser_position[0]=laser_blobs.x()+laser_blobs.w()/2
        laser_position[1]=laser_blobs.y()+laser_blobs.h()/2
        time.sleep_ms(50)
        #--------------图传-----------------------------
        img.draw_circle(corners[0][0],corners[0][1],2)
        img.draw_circle(corners[1][0],corners[1][1],2)
        img.draw_circle(corners[2][0],corners[2][1],2)
        img.draw_circle(corners[3][0],corners[3][1],2)
        img.draw_rectangle(laser_roi, color = (255, 0,0), scale = 2, thickness = 2)
        img.draw_circle(int(laser_blobs.x()+laser_blobs.w()/2),int(laser_blobs.y()+laser_blobs.h()/2),2, color = (0, 255, 0))
        break

#----------2D line---------------------------------------
Start_XY=[0,0]
slope=0
now_slope=0
def Les_2_Point(Target_XY):
    global Start_XY
    global slope
    global now_slope
    Start_XY=laser_position
    slope=(Target_XY[1]-laser_position[1])/(Target_XY[0]-laser_position[0])
    while(1):
        img = sensor.snapshot()
        Laser_Update(img)
        if (is_vision==1):
            if ((Target_XY[0]-laser_position[0])==0):
                now_slope=(Target_XY[1]-laser_position[1])*99  #avoid divide zero
            else:
                now_slope=(Target_XY[1]-laser_position[1])/(Target_XY[0]-laser_position[0])

            if (now_slope==0):
                now_slope=0.001   #avoid divide zero

            if laser_position[1]>Target_XY[1]:
                y_ex=-0.2
            elif laser_position[1]<Target_XY[1]:
                y_ex=0.2
            else:
                y_ex=0

            if laser_position[0]>Target_XY[0]:
                x_ex=0.2/abs(now_slope)
            elif laser_position[0]<Target_XY[0]:
                x_ex=-0.2/abs(now_slope)
            else:
                x_ex=0
            print(laser_position[0],laser_position[1],Target_XY[0],Target_XY[1],x_ex,y_ex)
            Servo_Excute([x_ex,y_ex],[10,10])

        if (abs(Target_XY[1]-laser_position[1]<=3))and (abs(Target_XY[0]-laser_position[0])<=3) :
            break


def Les_Reset():
    global Start_XY
    global slope
    global now_slope
    Start_XY=[0,0]
    slope=0
    now_slope=0

#=============主函数=========================
#plt.figure()
#plt.plot([0,1300], [0,0], linewidth=6)
#Point_2_Point(10,[0,0],[1300,0])
#plt.show()


clock = time.clock()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA2)
sensor.skip_frames(time = 1000)
Servo_Init()
Servo_X_Now_Ang=-25
Servo_Y_Now_Ang=5
s2.angle(-25)
s1.angle(5)

time.sleep_ms(2000)


Find_Rect()

Les_2_Point(corners[3])
Servo_Excute([0,0],[10,10])
time.sleep_ms(500)
Les_Reset()

Les_2_Point(corners[2])
Servo_Excute([0,0],[10,10])
time.sleep_ms(500)
Les_Reset()

Les_2_Point(corners[1])
Servo_Excute([0,0],[10,10])
time.sleep_ms(500)

Les_2_Point(corners[0])
Servo_Excute([0,0],[10,10])
time.sleep_ms(500)
Les_Reset()


#while(1):
    #img = sensor.snapshot()
    #Laser_Update(img)


