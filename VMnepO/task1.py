#****************������***********************
import numpy as np
import matplotlib.pyplot as plt
# import sensor, image, time
# from pyb import Servo
#=============��������======================
#------------PID����-----------------------
class PIDCtrl:
    def __init__(self, kp, ki, kd):
        self.__version__ = "0.0.1"
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.err = 0
        self.sum_err = 0
        self.last_err = 0
    #--------PID����----------------------
    def setErr(self, err):
        self.err = err
        self.sum_err += err
    #--------PID�ͳ�----------------------
    def output(self):
        out = self.kp * self.err
        out += self.ki * self.sum_err
        out += self.kd * (self.err-self.last_err)
        self.last_err = self.err
        return out

PID_Laser_2_Point=PIDCtrl(1,0,0)

#------------��������-----------------------
reset_botton=0
task1_botton=0
task2_botton=0
task3_botton=0
#--------����1/2��Ǧ����̨����---------------
pencil_center=[0,0]  #ʹ��Ǧ��ָ�����ĵĶ���Ƕ�
pencil_lu=[0,0]      #left / up
pencil_ru=[0,0]
pencil_rd=[0,0]
pencil_ld=[0,0]
#--------����3/4������������---------------
laser_position=[0,0]                   #��ǰ�����λ��
rect_position=[[0,0],[0,0],[0,0],[0,0]]#ʶ�𵽵Ŀ��λ��

#--------����3/4�������ȥ����---------------

Servo_X_Death_Pixcel=5 #׼ȷ����Ŀ������Ų�������
Servo_Y_Death_Pixcel=5
Servo_X_Step_Pixcel=50  #���ܳ��ڿ�����Ų�������
Servo_Y_Step_Pixcel=50
Servo_X_Step_time=500  #��׼��һ��step������������ʱ��
Servo_Y_Step_time=500
#============��������=======================
#------------��ť��ʼ��---------------------
def Button_Init(botton):
    reset_botton=botton[0]
    task1_botton=botton[1]
    task2_botton=botton[2]
    task3_botton=botton[3]
#------------��ȡ��ťֵ---------------------
def Button_Get():
    reset_botton=0
    task1_botton=0
    task2_botton=0
    task3_botton=0
#-------------�����ʼ��--------------------
# def Servo_Init(serv):
    # global s1
    # global s2
    # s1 = Servo(1)#P7
    # s2 = Servo(2)#P8
#--------------��̨�ƶ�---------------------
def Servo_Excute(angle,time):
    s1_now=s1.angle()
    s2_now=s2.angle()
    s1.angle(s1_now+angle[0],time[0])
    s2.angle(s2_now+angle[1],time[1])
#------------����λ�û�ȡ-------------------
laser_roi=[0,0,128,160]
laser_roi_wh=60 
laser_thresholds=[(61, 78, 19, 50, -39, 68)]   #����LABɫ��ֵ

def Laser_Update(img):
    for laser_blobs in img.find_blobs(laser_thresholds,pixels_threshold=1, area_threshold=1, merge=True,invert = 0,roi=task2_roi):
        laser_roi[0]=laser_blobs.x()-laser_roi_wh/2
        laser_roi[1]=laser_blobs.y()-laser_roi_wh/2
        laser_roi[2]=laser_roi_wh
        laser_roi[3]=laser_roi_wh
        laser_position=[laser_blobs.x()+laser_blobs.w()/2,laser_blobs.y()+laser_blobs.h()/2]
        time.sleep_ms(50)
        #--------------ͼ��-----------------------------
        img.draw_rectangle(laser_roi, color = (255, 0,0), scale = 2, thickness = 2)
        img.draw_circle(laser_blobs.x()+laser_blobs.w()/2,laser_blobs.y()+laser_blobs.h()/2,2, color = (0, 255, 0))
        img.draw_circle(40,40,2,color=(0,255,255))
        img.draw_circle(90,90,2,color=(0,255,255))
        break

#--------------�����ƶ�---------------------
L2P_steps=1#��ǰ�ܵ�
L2P_states=0#��ǰ�Ƿ�����ܵ�
Las_slope=0#��ǰ��������һ�����б��
P2P_slope=0#��ʼб��
Las_speed=[0,0]#��ǰӦ���͸�����ĽǶ�����
Las_enter=3#����Ŀ�������ٸ����ص�ʱ��ת������һstep
P2P_div=0#�ֻܷ���
Run_Map=[[0,0] for i in range(50)]
def Point_2_Point(std_speed,Start_XY,Target_XY):#std_speed��������ٶ�
    global L2P_steps
    global L2P_states#��ǰ�Ƿ�����ܵ�
    global Las_slope#��ǰ��������һ�����б��
    global P2P_slope#��ʼб��
    global Las_speed#��ǰӦ���͸�����ĽǶ�����
    global Las_enter#����Ŀ�������ٸ����ص�ʱ��ת������һstep
    global P2P_div#�ֻܷ���
    global Run_Map

    P2P_slope=(Target_XY[1]-Start_XY[1])/(Target_XY[0]-Start_XY[0])#������ʼ��б��

    Len_X=abs(Target_XY[0]-laser_position[0]-2*Servo_X_Death_Pixcel)#����XY�᳤��
    Len_Y=abs(Target_XY[1]-laser_position[1]-2*Servo_Y_Death_Pixcel)
    if (Target_XY[0]>laser_position[0]):                            #����XY���˶�����
        dir_X=1
    else:
        dir_X=-1
    if (Target_XY[1]>laser_position[1]):
        dir_Y=1
    else:
        dir_Y=-1    

    div_X=(Len_X // Servo_X_Step_Pixcel)                            #����XY��ֻ���Ŀ
    div_Y=(Len_Y // Servo_Y_Step_Pixcel)
    if (Len_X<=Len_Y):                                              #��С�������֣���ɷֻ� 
        Run_Map[1][0]=laser_position[0]+dir_X*Servo_X_Death_Pixcel
        Run_Map[1][1]=laser_position[1]+dir_Y*Servo_X_Death_Pixcel*P2P_slope
        P2P_div=div_X+2

        for index in range(2,div_X):
            Run_Map[index][0]=Run_Map[index-1][0]+dir_X*Servo_X_Step_Pixcel
            Run_Map[index][1]=Run_Map[index-1][1]+dir_Y*Servo_X_Step_Pixcel*P2P_slope

        Run_Map[div_X+1][0]=Target_XY[0]-dir_X*Servo_X_Death_Pixcel
        Run_Map[div_X+1][1]=Target_XY[1]-dir_Y*Servo_X_Death_Pixcel*P2P_slope

        Run_Map[div_X+2][0]=Target_XY[0]
        Run_Map[div_X+2][1]=Target_XY[1]

    else:
        Run_Map[1][1]=laser_position[1]+dir_Y*Servo_Y_Death_Pixcel
        Run_Map[1][0]=laser_position[0]+dir_X*Servo_Y_Death_Pixcel/P2P_slope
        P2P_div=div_Y+2

        for index in range(2,div_Y):
            Run_Map[index][1]=Run_Map[index-1][1]+dir_Y*Servo_Y_Step_Pixcel
            Run_Map[index][0]=Run_Map[index-1][0]+dir_X*Servo_Y_Step_Pixcel/P2P_slope

        Run_Map[div_X+1][1]=Target_XY[1]-dir_Y*Servo_Y_Death_Pixcel
        Run_Map[div_X+1][0]=Target_XY[0]-dir_X*Servo_Y_Death_Pixcel/P2P_slope

        Run_Map[div_Y+2][0]=Target_XY[0]
        Run_Map[div_Y+2][1]=Target_XY[1]

    while (L2P_steps<=P2P_div):
        plt.plot(Run_Map[L2P_steps][0],Run_Map[L2P_steps][1],'o')
        L2P_steps=L2P_steps+1

    # while (L2P_steps<=P2P_div):                             #�����Էֻ���ΪĿ��
    #     img = sensor.snapshot()
    #     clock.tick()
    #     Laser_Update(img)
    #     L2P_states=0                                        #����Ŀ���������������ݵ�ǰ������Ŀ�꣬���ú�XY���ٶ�
    #     Las_slope=(Run_Map[L2P_steps][1]-laser_position[1])/(Run_Map[L2P_steps][0]-laser_position[0]) 
    #     if ((Run_Map[L2P_steps][0]-laser_position[0])<(Run_Map[L2P_steps][1]-laser_position[1])):#������Ϊstd
    #         Las_speed[1]=std_speed
    #         Las_speed[0]=std_speed/Las_slope
    #     else: 
    #         Las_speed[0]=std_speed
    #         Las_speed[1]=std_speed*Las_slope
        
    #     while(L2P_states==0):                               #ִ��Ŀ�꣬���ж��Ƿ����
    #         img = sensor.snapshot()
    #         clock.tick()
    #         Laser_Update()
    #         Servo_Excute([Las_speed[0],Las_speed[1]],[Servo_X_Step_time,Servo_X_Step_time])
    #         if ((laser_position[0]+dir_X*Las_enter>=Run_Map[L2P_steps][0]) and (laser_position[1]+dir_Y*Las_enter>=Run_Map[L2P_steps][1])):
    #             L2P_states=1
    #             L2P_steps=L2P_states+1

#=============������=========================
plt.figure()
plt.plot([0,20], [0,1300], linewidth=6)      
Point_2_Point(10,[0,0],[20,1300])
plt.show()


# clock = time.clock()
# sensor.reset()
# sensor.set_pixformat(sensor.RGB565)
# sensor.set_framesize(sensor.QQVGA2)
# sensor.skip_frames(time = 1000)
# s1.angle(-10)
# s2.angle(-20)
# time.sleep_ms(2000)
# img = sensor.snapshot()
# Laser_Update(img)
# Point_2_Point(10,laser_position,[90,90])
        
