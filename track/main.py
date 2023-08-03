from find_bb import *
from find_loc import *
from pid import *
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

px=PID(0.01,0,0.005)
py=PID(0.01,0,0.005)

x=325
y=325

def move(ct,cn):
    cnx,cny=cn
    ctx,cty=ct
    global x,y
    x+=px.output(cnx-ctx)
    y-=py.output(cny-cty)
    print('x=',x,'   y=',y)
    if x<200:
        x=200
    if x>400:
        x=400
    if y<295:
        y=295
    if y>340:
        y=340
    pwm.set_pwm(5,0,int(x))  # 底座舵机
    pwm.set_pwm(4,0,int(y))  # 倾斜舵机


def main():
    # 打开摄像头
    cap = cv2.VideoCapture(0)  # 参数0表示使用默认摄像头，如果有多个摄像头，可以逐个尝试参数1、2、3...

    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        print("无法打开摄像头。请检查是否连接了正确的摄像头设备。")
        return



    while True:
        ret, frame = cap.read()

        if not ret:
            print("无法获取视频帧。")
            break

        # 在每一帧上找到黑色块的中心
        # ct = fbb(frame)

        ct=(320,240)

        if ct:
            center_x, center_y = ct
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # 在中心点处画一个红色的圆

        cn=floc(frame)

        if cn:
            center_x, center_y = cn
            print('nx=',center_x,'   ny=',center_y)
            cv2.circle(frame, (center_x, center_y), 5, (255, 0,0), -1)  # 在中心点处画一个红色的圆

        cv2.imshow("Black Blob Center Detection", frame)
        
        

        move(ct,cn)

        # 按 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
