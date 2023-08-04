from find_red import *
from get_rec import *
from pid import *
import Adafruit_PCA9685

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

px=PID(0.02,0,0.01)
py=PID(0.02,0,0.01)

x=325
y=302


pwm.set_pwm(5,0,x)  # 底座舵机   290     370左
pwm.set_pwm(4,0,y)  # 倾斜舵机   260     350  下  

def move(ct,cn):
    cnx,cny=cn
    ctx,cty=ct
    global x,y
    ex=cnx-ctx
    ey=cny-cty
    if abs(ex) < 4:
        ex=0
    if abs(ey) < 4:
        ey=0
    if ex==0 and ey == 0:
        
        return 1
    x+=px.output(ex)
    y-=py.output(ey)
    print('x=',x,'   y=',y)
    if x<290:
        x=290
    if x>370:
        x=370
    if y<260:
        y=260
    if y>350:
        y=350
    pwm.set_pwm(5,0,int(x))  # 底座舵机
    pwm.set_pwm(4,0,int(y))  # 倾斜舵机

    return 0


def main():
    # 打开摄像头
    cap = cv2.VideoCapture(0)  # 参数0表示使用默认摄像头，如果有多个摄像头，可以逐个尝试参数1、2、3...

    cap.set(3, 640)
    cap.set(4, 480)

    if not cap.isOpened():
        print("无法打开摄像头。请检查是否连接了正确的摄像头设备。")
        return

    corners=[]

    while len(corners)!=4:
        ret, image = cap.read()

        image=image[125:400,230:500]

        corners=drec(image)
        
    #当前顶点  vi
    vi = 0

    while True:
        pf=1
        ret, image = cap.read()

        image=image[125:400,230:500]

        if not ret:
            print("无法获取视频帧。")
            break


        # corners=drec(image)
        for cor in corners:
            cv2.circle(image, (cor[0], cor[1]), 5, (255, 0, 0), -1)

        ct=corners[vi]
        print('tx=',corners[vi][0],'   ty=',corners[vi][1])

        # if ct:
        #     cx, cy = ct
        #     cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)  # 在中心点处画一个红色的圆

        cn=fr(image)

        if cn:
            cx, cy = cn
            if cx or cy:
                print('nx=',cx,'   ny=',cy)
                cv2.circle(image, (cx, cy), 5, (0, 255,0), -1)  # 在中心点处画一个红色的圆
            else :
                pf=0

        
        cv2.imshow("Black Blob Center Detection", image)

        if pf:
            if move(ct,cn):
                print('====================OK==============================')
                vi=(vi+1)%4

        # 按 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
