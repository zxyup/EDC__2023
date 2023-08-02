import sensor, image, time

from pid import PID
from pyb import Servo			#调用库

pan_servo=Servo(1)
tilt_servo=Servo(2)


red_threshold  = (0, 98, 37, 127, -32, 89)				#红色色素块

pan_pid = PID(p=0.06,i=0.1, imax=90) #脱机运行或者禁用图像传输，使用这个PID
tilt_pid = PID(p=0.05,i=0.05, imax=90) #脱机运行或者禁用图像传输，使用这个PID
#pan_pid = PID(p=0.06,d=0.01,i=0.02, imax=100)#在线调试使用这个PID
#tilt_pid = PID(p=0.07,d=0.01,i=0.02, imax=75)#在线调试使用这个PID
#pan_pid = PID(p=0.06,d=0,i=0, imax=100)#在线调试使用这个PID
#tilt_pid = PID(p=0.07,d=0,i=0, imax=75)#在线调试使用这个PID
    #由于openmv脱机运行帧率会提高，运行性能会有所改变，所以需要设置“在线联机调试”和“脱机运行”的两个参数

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.						#基本参数设置

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob											#找到视野中的最大色素块


while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.

    blobs = img.find_blobs([red_threshold])					#biob函数的详细内容可去星瞳科技的官网查询
    if blobs:
        max_blob = find_max(blobs)
    #    pan_error = max_blob.cx()-img.width()/2
   #     tilt_error = max_blob.cy()-img.height()/2

        pan_error = img.width()/2-max_blob.cx()					#	横轴方向上的修正参数
        tilt_error = img.height()/2-max_blob.cy()			   		#	纵轴方向上的修正参数
      #  pan_error = 80+max_blob.cx()
     #   tilt_error = 60+max_blob.cy()


        print("pan_error: ", pan_error)			#在参数调试窗口打印色块中心坐标与视野中心坐标的偏离值，便于调试与修正

        img.draw_rectangle(max_blob.rect()) # rect					#在色块外围四周处画框
        img.draw_cross(max_blob.cx(), max_blob.cy()) # cx, cy     #色块中心坐标处画十字

        pan_output=pan_pid.get_pid(pan_error,1)/2
        tilt_output=tilt_pid.get_pid(tilt_error,1)/2
        print("pan_output",pan_output)		  	     #在参数调试窗口打印坐标值，便于调试与修正
        pan_servo.angle(pan_servo.angle()+pan_output)			#输出横轴方向上的PWM波控制云台追踪色块标志
                                                        #openmv上P7为控制云台上舵机的输出引脚（摄像头上下移动）
        tilt_servo.angle(tilt_servo.angle()-tilt_output)		#输出纵轴方向上的PWM波控制云台追踪色块标志
                                                         #openmv上P8为控制云台下舵机的输出引脚（摄像头左右移动）
