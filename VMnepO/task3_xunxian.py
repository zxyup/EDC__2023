#****************包声明***********************
#import numpy as np
#import matplotlib.pyplot as plt
import sensor,image,time,pyb
from pyb import Servo
from pyb import Pin
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
    #--------PID送出----------------------
    def output(self, err):
        self.err = err
        self.sum_err += err
        out = self.kp * self.err
        out += self.ki * self.sum_err
        out += self.kd * (self.err-self.last_err)
        self.last_err = self.err
        return out

PID_Laser_2_Point=PIDCtrl(1,0,0)

#------------交互变量-----------------------
reset_botton=0
pause_botton=0
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

#============函数声明=======================
#------------按钮初始化---------------------
key3=0
key1=0
key2=0
key_count=0

def callback_PIN2(line):
    global key2
    key2=1
    pyb.delay(5)

def callback_PIN3(line2):
    global key3
    key3=1
    pyb.delay(5)

def Button_Init():
    global p_in3
    global p_in1
    global p_in2
    p_in3 = Pin('P3', Pin.IN, Pin.PULL_NONE)
    p_in1 = Pin('P1', Pin.IN, Pin.PULL_NONE)
    p_in2 = Pin('P2', Pin.IN, Pin.PULL_NONE)
    extint = pyb.ExtInt(p_in2, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_NONE, callback_PIN2)
    extint = pyb.ExtInt(p_in3, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_NONE, callback_PIN3)
    key2=0
#-------------舵机初始化--------------------
def Servo_Init():
     global s1
     global s2
     global xx
     global yy
     global x
     global y
     s1 = Servo(1)#P7
     s2 = Servo(2)#P8
     y=Servo(1)
     x=Servo(2)
     y.angle(0)
     x.angle(0)
     xx=x.pulse_width()
     yy=y.pulse_width()
     px=PIDCtrl(0.2,0,0)
     py=PIDCtrl(0.2,0,0)

#------------Servo Output----------------------------
def move(ct,cn):
    cnx,cny=cna
    ctx,cty=ct
    global xx,yy
    xx+=px.output(cnx-ctx)
    yy-=py.output(cny-cty)
    print('x_pulse=',xx,'y_pulse=',yy,'tar pic_x=',ct[0],'tar pic_y=',ct[1])
    if xx<950:
        xx=950
    if xx>1750:
        xx=1750
    if yy<1060:
        yy=1060
    if yy>1800:
        yy=1800
    y.pulse_width(int(yy))
    x.pulse_width(int(xx))
    if (abs(ct[0]-cn[0])<5) and (abs(ct[1]-cn[1])<5):
        return 1
    else:
        return 0

#------------框点获取--------------------
def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob

task3_rect_thresholds=40                       #长宽大于40像素的框，才被视为有效的黑框
task3_rect_max_thres=10000                     #长度小于10000像素的框，才被视为有效的黑框
corners=[[0,0],[0,0],[0,0],[0,0]]
Rec_Roi=[20,15,90,110]
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

    #while(find_rect_count<=59):
    print(find_rect_count)
    img = sensor.snapshot()
    blobs =  img.find_rects(roi=Rec_Roi,threshold = 10000) #识别矩形框
    max_blob = find_max(blobs)
    corners=max_blob.corners()

#------------激光位置获取-------------------
laser_roi=[0,0,128,160]
laser_roi_wh=30
#laser_thresholds=[(61, 78, 19, 50, -39, 68)]   #激光LAB色块值
laser_thresholds=[(100, 0, 127, 36, -21, 15)]
#laser_thresholds=[(75, 93, -107, 127, -128, 127)]#out black detect
is_laser_vision=0  #是否有看到激光
def Laser_Update(img):
    global is_vision
    is_laser_vision=0
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
        img.draw_circle(int(laser_blobs.x()+laser_blobs.w()/2),int(laser_blobs.y()+laser_blobs.h()/2),2, color = (0, 255, 0))
        break
def draw_help():
    img.draw_circle(corners[0][0],corners[0][1],2)
    img.draw_circle(corners[1][0],corners[1][1],2)
    img.draw_circle(corners[2][0],corners[2][1],2)
    img.draw_circle(corners[3][0],corners[3][1],2)
    img.draw_rectangle(laser_roi, color = (255, 0,0), scale = 2, thickness = 1)
    img.draw_rectangle(Rec_Roi, color = (255, 0,0), scale = 2, thickness = 1)

##----------指引激光移动到固定点位(扫描法）---------------------------------------
#Start_XY=[0,0]
#slope=0
#now_slope=0
#Las_std_speed=0.2
#x_pid=PIDCtrl(0.01,0,0)
#y_pid=PIDCtrl(0.01,0,0)

#def Las_2_Point(Target_XY):
    #global Start_XY
    #global slope
    #global now_slope
    #Start_XY=laser_position
    #slope=(Target_XY[1]-laser_position[1])/(Target_XY[0]-laser_position[0])

    #while(1):
        #img = sensor.snapshot().lens_corr(strength=1.8, zoom=1.0)
        #Laser_Update(img)
        #draw_help()
        #if (is_vision==1):
            ##--------------计算当前斜率与前进方向-------------------------------------------
            #if ((Target_XY[0]-laser_position[0])==0):
                #now_slope=(Target_XY[1]-laser_position[1])*99  #避免除以0
            #else:
                #now_slope=(Target_XY[1]-laser_position[1])/(Target_XY[0]-laser_position[0])
            #if (now_slope==0):
                #now_slope=0.001   #避免除以0

            #if (Target_XY[0]>=laser_position[0]):
                #dir_x=-1
            #else:
                #dir_x=1

            #if (Target_XY[1]>=laser_position[1]):
                #dir_y=1
            #else:
                #dir_y=-1
            ##---------------斜率半开环-------------------------------------------
            #if ((Target_XY[1]-laser_position[1])>=(Target_XY[0]-laser_position[0])):#X边长最短,故以Y为扫描速度
                #y_ex=Las_std_speed*dir_y
                #x_ex=0.1/abs(now_slope)*dir_x
            #else:
                #x_ex=Las_std_speed*dir_x
                #y_ex=0.1*abs(now_slope)*dir_y

            #print(laser_position[0],laser_position[1],Target_XY[0],Target_XY[1],x_ex,y_ex)
            ##------------------斜率闭环------------------------------------------
            #x_ex=x_pid.output(Target_XY[0]-laser_position[0])*-1
            #y_ex=y_pid.output(Target_XY[1]-laser_position[1])*-1
            ##---------------负反馈输出--------------------------------------------
            #Servo_Excute([x_ex,y_ex],[10,10])
        ##--------------------循迹停止--------------------------------------
        #if (abs(Target_XY[1]-laser_position[1]<=4))and (abs(Target_XY[0]-laser_position[0])<=4) :
            #break
#def Las_Reset():
    #global Start_XY
    #global slope
    #global now_slope
    #Start_XY=[0,0]
    #slope=0
    #now_slope=0
#--------------散点直线移动---------------------
L2P_steps=1#当前跑点
P2P_div=0#总分划数
Run_Map=[[0,0] for i in range(500)]
Servo_Death_Pixcel = 10#最小可移动像素
Servo_Task_State=0     #是否完成单个跑点

def Point_2_Point(Start_XY,Target_XY):
    #--------------线段特征初始化-------------------------------
    start_k=(Target_XY[1]-Start_XY[1])/(Target_XY[0]-Start_XY[0])
    start_b=Target_XY[1]-start_k*Target_XY[0]

    len_x=Target_XY[0]-Start_XY[0]
    len_y=Target_XY[1]-Start_XY[1]

    div_x=len_x // Servo_Death_Pixcel
    div_y=len_y // Servo_Death_Pixcel
    if (Start_XY[0]<=Target_XY[0]):
        dir_x=1
    else:
        dir_x=-1

    if (Start_XY[1]<=Target_XY[1]):
        dir_y=1
    else:
        dir_y=-1
    #---------------绘制散点----------------------------
    if (len_x<=len_y):
        P2P_div=div_y
        for index in range(1,P2P_div):
            Run_Map[index][1]=(Start_XY[1]+index*dir_y*Servo_Death_Pixcel)
            Run_Map[index][0]=((Run_Map[index][1]-start_b)/start_k)
        Run_Map[P2P_div+1]=Target_XY
        P2P_div+=1
    else:
        P2P_div=div_x
        for index in range(1,P2P_div):
            Run_Map[index][0]=(Start_XY[0]+index*dir_x*Servo_Death_Pixcel)
            Run_Map[index][1]=((Run_Map[index][0]*start_k+start_b))
        Run_Map[P2P_div+1]=Target_XY
        P2P_div+=1
    #---------------执行散点-----------------------------
    for L2P_steps in range(1,P2P_div):
        Servo_Task_State=0
        while(Servo_Task_State==0):
            img = sensor.snapshot()
            Laser_Update(img)
            draw_help()
            Servo_Task_State=move(Run_Map[L2P_steps],laser_position)
        time.sleep_ms(500)







#=============主函数=========================
#clock = time.clock()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA2)
#sensor.set_framesize(sensor.QVGA)
#sensor.set_auto_gain(1)
sensor.set_auto_exposure(False, exposure_us=800)
#sensor.set_auto_whitebal(0)
sensor.skip_frames(400)
Servo_Init()
Button_Init()
print("Init Over")
#--------------------------------------------
#Find_Rect()
print("Find Over")



#-----------------------------------------------
while(1):
#=================KEY3====================================
    if key3==1 and p_in3.value()==0:
        key_count+=1
        print("Pause2!",key_count)
        key3=0

        #-------------------------------------------
        if (key_count==1):
            print("Start Task 1?")
        #-------------------------------------------
        elif (key_count==2):
            print("Start Task 2?")
        #-------------------------------------------
        elif (key_count==3):
            print("Start Task 3?")
        #-------------------------------------------
        elif (key_count==4):
            print("Start Task 4?")
            Find_Rect()
            state=0
            img = sensor.snapshot()
            Laser_Update(img)
            Point_2_Point(laser_position,corners[2])
            time.sleep_ms(3000)
            Point_2_Point(laser_position,corners[3])
            time.sleep_ms(3000)
            Point_2_Point(laser_position,corners[0])
            time.sleep_ms(3000)
            Point_2_Point(laser_position,corners[1])
            time.sleep_ms(3000)

#=================KEY1====================================
    if p_in1.value()==0:
        print("Reset?")
        x.angle(0)
        y.angle(0)
        key1=0
#=================KEY2====================================
    if key2==1 and p_in2.value()==0:
        print("Pause!")
        key2=0

    #img = sensor.snapshot()
    #Laser_Update(img)
    time.sleep_ms(60)
    #if state==0:
        #state+=move(corners[2],laser_position)
    #elif state==1:
        #state+=move(corners[3],laser_position)
    #elif state==2:
        #state+=move(corners[0],laser_position)
    #elif state==3:
        #state+=move(corners[1],laser_position)
    #elif state==4:
        #state=0





