#****************包声明***********************
import sensor, image, time
from pyb import Servo
#****************类初始化**********************
#==================PID类======================
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
#===============任务二=========================
class Task2_Rect_Finder:
    #----------初始化方法--------------------
    def Set_Rect_Corner(self,corners):
        self.corner1=corners[0]
        self.corner2=corners[1]
        self.corner3=corners[2]
        self.corner4=corners[3]

    def Set_Laser_XY(self,Laser_X_Pixcel,Laer_Y_Pixcel):
        self.Laser_X=Laser_X_Pixcel
        self.Laser_Y=Laer_Y_Pixcel

    def Set_PID(self,Px,Ix,Dx,Py,Iy,Dy):
        self.PIDx=PIDCtrl(Px,Ix,Dx)
        self.PIDy=PIDCtrl(Py,Iy,Dy)

    def Config_Servo(self,Servo_X,Servo_Y):
        self.Servo_X=Servo_X
        self.Servo_Y=Servo_Y
    #---------功能方法------------------------
    def turn_to_corner1(self):
        (self.PIDx).setErr(self.corner1[0]-self.Laser_X)
        X_out=(self.PIDx).output()
        Y_out=(self.PIDy).output()

        if (X_out<0.5):
            X_out=(self.Servo_X).angle()+0.5
        else:
            X_out=(self.Servo_X).angle()+X_out

        if (Y_out<0.5):
            Y_out=(self.Servo_Y).angle()+0.5
        else:
            Y_out=(self.Servo_Y).angle()+Y_out

        (self.Servo_X).angle(X_out)
        (self.Servo_Y).angle(Y_out)
        print("Task2:X_Out=",X_out,"Y_out=",Y_out)

    def corner_to_corner(basic_speed,cor_index_1,cor_index_2):
        X_out=basic


#--------------对象初始化-------------------
clock = time.clock()
s1 = Servo(1)
s2 = Servo(2)
task1_pid = PIDCtrl(10, 0, 0)

Task2=Task2_Rect_Finder()

#--------------参数初始化-------------------
task1_left_angle=30
task1_up_angle=30
task1_right_angle=-30
task1_down_angle=-30
task1_state=0

task2_rect_thresholds=20
task2_roi=[34,50,30,30]
laser_thresholds=[(61, 78, 19, 50, -39, 68)]



#==============MV初始化======================
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA2)
sensor.skip_frames(time = 3000)
print("OpenMV:Width=",sensor.width())#128
print("OpenMV:height=",sensor.height())#160

s1.angle(0)
s2.angle(0)

Task2.Set_Laser_XY(64,64)
Task2.Set_PID(0.5,0,0,0.5,0,0)
Task2.Config_Servo(s1,s2)
#=============任务2.2========================
while(True):
    img = sensor.snapshot()
    clock.tick()
    #----------------------找黑框--------------------------------
    for r in img.find_rects(threshold = 10000):
        if r.w() > task2_rect_thresholds and r.h() > task2_rect_thresholds:
            corners=r.corners()
            Task2.Set_Rect_Corner(corners)
            #-----------------------------------------
            img.draw_rectangle(task2_roi, color = (255, 0,0), scale = 2, thickness = 2)
            img.draw_circle(corners[0][0], corners[0][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corners[1][0], corners[1][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corners[2][0], corners[2][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
            img.draw_circle(corners[3][0], corners[3][1], 5, color = (0, 0, 255), thickness = 2, fill = False)
    #-----------------------找激光------------------------------
    for laser_blobs in img.find_blobs(laser_thresholds,pixels_threshold=1, area_threshold=1, merge=True,invert = 0,roi=task2_roi):
        #------------找到激光了----------------------------------
        task2_roi[0]=laser_blobs.x()-10
        task2_roi[1]=laser_blobs.y()-10
        Task2.Set_Laser_XY(laser_blobs.x(),laser_blobs.y())

        Task2.turn_to_corner1()
        #------------------------------------------------------
        img.draw_rectangle(laser_blobs.x(),laser_blobs.y(),3,3, color = (0, 255, 0), scale = 2, thickness = 2)
        break


# -----跟踪激光部分-----
    # 设置激光颜色阈值
    #red_td = [(61, 78, 19, 50, -39, 68)]
    # 根据阈值找到色块
    #for c in img.find_circles(threshold = 1000, x_margin = 10, y_margin = 10, r_margin = 10,
     #       r_min = 0, r_max = 80, r_step = 1):
      #  if c.r()<7:
       #     img.draw_circle(c.x(),c.y(),c.r()+5)
        #    for b in img.find_blobs(red_td,pixels_threshold=2, area_threshold=15, merge=True,invert = 0):
                # 在屏幕上画出色块
          #      img.draw_rectangle(b.rect(), color = (0, 255, 0), scale = 2, thickness = 2)
         #       break
                #redx=b.x()+b.w()/2
               # redy=b.y()+b.h()/2
                #print('red',redx,redy)

    # 打印帧率
    #print(clock.fps())

