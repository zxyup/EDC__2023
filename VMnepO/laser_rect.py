#****************包声明***********************
import sensor, image, time
from pyb import Servo
#****************类初始化**********************

#==================PID类======================
#增量式PID：给定当前值和目标值，返回输出值所需的增量
#绝对式PID：给定当前值和目标值，返回输出值
#绝对式PID还需要确定像素和舵机脉宽的关系，过于复杂，所以此处使用了增量式PID
#将目标坐标和当前激光坐标送入setErr后，通过output获取所需增量
#增量式和绝对式只是使用方法不相同，本质的PID方程依然相同，该PIDCtrl类一样可以用来写绝对式PID
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
#===============任务三的类=========================
class Task3_Laser:
    #----------初始化方法--------------------
    def Set_Rect_Corner(self,corners):
        self.corner1=corners[0]
        self.corner2=corners[1]
        self.corner3=corners[2]
        self.corner4=corners[3]

    def Update_Laser_XY(self,Laser_X_Pixcel,Laer_Y_Pixcel):
        self.Laser_X=Laser_X_Pixcel
        self.Laser_Y=Laer_Y_Pixcel

    def Set_PID(self,Px,Ix,Dx,Py,Iy,Dy):
        self.PIDx=PIDCtrl(Px,Ix,Dx)
        self.PIDy=PIDCtrl(Py,Iy,Dy)

    def Set_Servo(self,Servo_X,Servo_Y):
        self.Servo_X=Servo_X
        self.Servo_Y=Servo_Y
        self.Servo_Now_X=Servo_X.angle()
        self.Servo_Now_Y=Servo_Y.angle()

    def Update_Servo(self)
        self.Servo_Now_X=Servo_X.angle()
        self.Servo_Now_Y=Servo_Y.angle()
    #---------功能方法------------------------
    def laser_to_point(target_point):

        (self.PIDx).setErr(target_point[0]-self.Laser_X)
        (self.PIDy).setErr(target_point[1]-self.Laser_Y)
        PIDx=(self.PIDx).output()
        PIDy=(self.PIDy).output()

        self.Update_Servo()
        X_out=(self.Servo_X).Servo_Now_X+PIDx
        Y_out=(self.Servo_Y).Servo_Now_Y+PIDy

        (self.Servo_X).angle(X_out)
        (self.Servo_Y).angle(Y_out)

        if (PIDx<=0.1 and PIDy<=0.1):
            return 1
        else:
            return 0
    #-----------------------------------------
    def point_to_point(std_speed,over_line_gain,start_point,end_point):

        c2c_slope=(start_point[1]-end_point[1])/(start_point[0]-end_point[0])
        l2c_slope=(self.Laser_Y-start_point[1])/(self.Laser_X-start_point[0])
        #c2l_slope=(self.Laser_Y-end_point[1])/(self.Laser_X-end_point[0])

        if (c2c_slope>=1):
            X_out=std_speed
            Y_out=std_speed*c2c_slope
        elif (c2c_slope<=-1):
            X_out=-1*std_speed
            Y_out=std_speed*c2c_slope
        elif (c2c_slope>=0):
            Y_out=std_speed
            X_out=std_speed*c2c_slope
        elif (c2c_slop<0):
            Y_out=-1*std_speed
            X_out=std_speed*c2c_slope
        #------------闭环部分-----------------
        #if (l2c_slope>c2c_slope):#到起始点的斜率大于线段斜率
        #    Y_out=Y_out-over_line_gain#P控制
        #elif (l2c_slope<c2c_slope):#到起始点的斜率小于线段斜率
        #    Y_out=Y_out+over_line_gain#P控制
        #-----------------------------------

        if ((abs(self.Laser_Y-end_point[1])<=2) and (abs(self.Laser_X-end_point[0])<=2)):
            self.Update_Servo()
            Angle_out_X=(self.Servo_X).Servo_Now_X#定住
            Angle_out_Y=(self.Servo_Y).Servo_Now_Y
            (self.Servo_X).angle(Angle_out_X)
            (self.Servo_Y).angle(Angle_out_Y)
            return 1
        else:
            Angle_out_X=(self.Servo_X).Servo_Now_X+X_out#增量
            Angle_out_Y=(self.Servo_Y).Servo_Now_Y+Y_out
            (self.Servo_X).angle(Angle_out_X)
            (self.Servo_Y).angle(Angle_out_Y)
            return 0
#--------------对象初始化-------------------
clock = time.clock()
s1 = Servo(1)#P7
s2 = Servo(2)#P8
Task3=Task3_Laser()
#--------------参数初始化-------------------
task3_rect_thresholds=20                       #长宽大于20像素的框，才被视为有效的黑框
task3_rect_max_thres=10000                     #长度小于10000像素的框，才被视为有效的黑框
task3_roi=[0,0,128,160]                        #激光ROI初始值
laser_thresholds=[(61, 78, 19, 50, -39, 68)]   #激光LAB色块值
laser_roi_wh=60                                #激光roi框宽
#laser_thresholds=[(69, 32, 29, 118, -128, 127)]
task3_state=0                                  #任务case状态
Task3.Set_PID(0.006,0,0,0.006,0,0)             #激光移动到坐标的增量PID
#==============设备初始化======================
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA2)
sensor.skip_frames(time = 1000)

Task2.Config_Servo(s2,s1)                      #s2为X轴，S1为Y轴
s1.angle(-10)
s2.angle(-20)
time.sleep_ms(2000)

#***************任务3.1：找框******************************
for r in img.find_rects(threshold = task3_rect_max_thres):
        if r.w() > task3_rect_thresholds and r.h() > task3_rect_thresholds:
           corners=r.corners()
           Task3.Set_Rect_Corner(corners)
#***************任务3.2：巡线******************************
while(True):
        img = sensor.snapshot()
        clock.tick()
    #for r in img.find_rects(threshold = 1000):
        #if r.w() > task2_rect_thresholds and r.h() > task2_rect_thresholds:
           #corners=r.corners()
           #print("Find")
           #Task2.Set_Rect_Corner(corners)
           #img.draw_circle(Task2.corner1[0],Task2.corner1[1],2)
           #img.draw_circle(Task2.corner2[0],Task2.corner2[1],2)
           #img.draw_circle(Task2.corner3[0],Task2.corner3[1],2)
           #img.draw_circle(Task2.corner4[0],Task2.corner4[1],2)
        #-----------------------找激光------------------------------
        for laser_blobs in img.find_blobs(laser_thresholds,pixels_threshold=1, area_threshold=1, merge=True,invert = 0,roi=task2_roi):
            #------------更新激光参数------------------------------
            task3_roi[0]=laser_blobs.x()-laser_roi_wh/2
            task3_roi[1]=laser_blobs.y()-laser_roi_wh/2
            task3_roi[2]=laser_roi_wh
            task3_roi[3]=laser_roi_wh
            Task3.Update_Laser_XY(laser_blobs.x(),laser_blobs.y())
            #------------开环前往固定点----------------------------
            if (task3_state==0):
                print("Task3:state 0")
                if (Task3.laser_to_point([40,40]))==1：#先给固定的像素参数
                    task3_state=1
            #-------------闭环走点到点----------------------------
            elif (task3_state==1):
                print("Task3:state 1")
                if (Task3.point_to_point([40,40],[90,90]))==1：#先给固定的像素参数
                    task3_state=2
            #--------------无动作-------------------------------
            elif (task3_state==2):
                print("Task3:Over")


            #if laser_blobs.x()<=target_x:
                #XX=-2
            #elif laser_blobs.x()>=target_x:
                #XX=2
            #else :
                #XX=0
            #XX=XX+s2.angle()


            #if laser_blobs.y()<=target_y:
                #YY=-2
            #elif laser_blobs.y()>=target_y:
                #YY=2
            #else :
                #YY=0
            #YY=YY+s1.angle()

            #s2.angle(XX,550)
            #s1.angle(YY,550)

            #print("Laser=",laser_blobs.x(),"Target=",target_x,"Serv=",s2.angle(),"out=",XX)
            time.sleep_ms(50)
            #--------------图传-----------------------------
            img.draw_circle(Task3.corner1[0],Task3.corner1[1],2,(0,255,0),2)
            img.draw_circle(Task3.corner2[0],Task3.corner2[1],2,(0,255,0),2)
            img.draw_circle(Task3.corner3[0],Task3.corner3[1],2,(0,255,0),2)
            img.draw_circle(Task3.corner4[0],Task3.corner4[1],2,(0,255,0),2)

            img.draw_rectangle(task2_roi, color = (255, 0,0), scale = 2, thickness = 2)
            img.draw_circle(laser_blobs.x()+laser_blobs.w()/2,laser_blobs.y()+laser_blobs.h()/2,2, color = (0, 255, 0))
            img.draw_circle(40,40,2,color=(0,255,255))
            img.draw_circle(90,90,2,color=(0,255,255))
            break




