import cv2
import numpy as np
import time

def filter(data):
    # 将数据转换为NumPy数组
    data_array = np.array(data)

    # 使用numpy.bincount()计算每个唯一元素的出现次数
    counts = np.bincount(data_array)

    # 找到出现次数最多的元素的索引
    mode_index = np.argmax(counts)

    # 获取众数的值
    mode_value = mode_index

    return mode_value


def fr(image):
    # 将图像转换为HSV颜色空间
    grid_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 
    # 从RGB色彩空间转换到HSV色彩空间
    grid_HSV = cv2.cvtColor(grid_RGB, cv2.COLOR_RGB2HSV)
 
    # H、S、V范围一：
    lower1 = np.array([0,43,46])
    upper1 = np.array([10,255,255])
    mask1 = cv2.inRange(grid_HSV, lower1, upper1)       # mask1 为二值图像
    res1 = cv2.bitwise_and(grid_RGB, grid_RGB, mask=mask1)
 
    # H、S、V范围二：
    lower2 = np.array([156,43,46])
    upper2 = np.array([180,255,255])
    mask2 = cv2.inRange(grid_HSV, lower2, upper2)
    res2 = cv2.bitwise_and(grid_RGB,grid_RGB, mask=mask2)
 
    # 将两个二值图像结果 相加
    mask3 =  mask2
    
    # 结果显示
    # cv2.imshow("mask3", mask3)
    # cv2.waitKey(0)

    # 检测红色点的位置
    red_points = cv2.findNonZero(mask3)
    # print(red_points)
    
    x=0
    y=0

    if red_points is not None:
        for point in red_points:
            tx, ty = point[0]
            x+=tx
            y+=ty
        x=x//len(red_points)
        y=y//len(red_points)
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

    return x,y


def frf(image,s=10):
    x=[]
    y=[]
    for i in range(10):
        tx,ty=fr(image)
        x.append(tx)
        y.append(ty)
    sx=filter(x)
    sy=filter(y)
    return sx,sy


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头。请检查是否连接了正确的摄像头设备。")
        return

    start_time = time.time()
    image_count = 0

    while True:
        ret, image = cap.read()
        # print(image.shape)    # x 640 y 480
        
        image=image[125:400,230:500]  #[y1:y2,x1:x2]

        # cv2.imwrite('0.jpg',image)
        # return 

        if not ret:
            print("无法获取视频帧。")
            break

        fr(image)

        image_count += 1
        current_time = time.time()
        elapsed_time = current_time - start_time
        fps = image_count / elapsed_time

        # 在视频帧上绘制帧率信息
        cv2.putText(image, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Video", image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
