THRESHOLD = (0, 20, -128, 127, -128, 127) # Grayscale threshold for dark things...
import sensor, image, time
from pyb import UART,LED
from pid import PID
import ustruct
rho_pid = PID(p=0.17, i=0 , d=0)#y=ax+b b截距
theta_pid = PID(p=0.001, i=0, d=0)#a斜率


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA) # 80x60 (4,800 pixels) - O(N^2) max = 2,3040,000.
sensor.skip_frames(time = 2000)     # 跳过2s帧
clock = time.clock()                # to process a frame sometimes.

uart = UART(3,115200)   #定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1) # init with given parameters
#def sending_data(xw):
    #global uart;
    #data = ustruct.pack("<bbib",
                   #0x2C,                      #帧头1
                   #0x12,                      #帧头2
                   #int(xw), # up sample by 4   #数据1
                   #0x5B)
    #uart.write(data);   #必须要传入一个字节数组
def sending_data(x,y,z):
    global uart;
    data = bytearray([0x2C,0x12,int(x),int(y),int(z),0x5B])
    uart.write(data);   #必须要传入一个字节数组

while(True):
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD])#线设置为白色，其他为黑色
    line = img.get_regression([(100,100)], robust = True)#返回直线蓝色
    if (line):
        rho_err = abs(line.rho())-img.width()/2#直线偏移距离
        if line.theta()>90:#直线角度
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()
        img.draw_line(line.line(), color = 127)#画出蓝色直线
        #print(rho_err,line.magnitude(),rho_err)
        if line.magnitude()>8:#线性回归效果，好进行下一步，否则不进行s
            #if -40<b_err<40 and -30<t_err<30:
            rho_output = rho_pid.get_pid(rho_err,1)
            theta_output = theta_pid.get_pid(theta_err,1)
            xw = rho_output+theta_output
        else:
            xw=0.0
    else:
        xw=-404.0
        pass
    print((xw*1000+4040)/50.5)
    sending_data((xw*1000+4040)/50.5,0,1)
    #FH = ustruct.pack("<bbib",      #格式为俩个字符俩个短整型(2字节)
                               #0x2C,                      #帧头1
                               #0x12,                      #帧头2
                               #int(xw*1000), # up sample by 4   #数据1
                               #0x5B)
    #uart.write(FH)
