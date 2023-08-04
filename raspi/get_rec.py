import cv2
import numpy as np
import time



def drec(image):
    cors8=[]
    cors4=[]
    # 读取图像并转换为灰度图
    # print(image.shape)
    # cv2.imshow('Rectangles', image)
    # cv2.waitKey(0)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 边缘检测
    # edges = cv2.Canny(gray, threshold1, threshold2)


    _, edges = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    edges=255-edges

    # cv2.imshow('Rectangles', edges)
    # cv2.waitKey(0)

    # 轮廓检测
    contours, _ = cv2.findContours(edges,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选矩形轮廓
    rectangles = []
    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        if len(approx) == 4:
            for vertex in approx:
                # print(type(vertex))
                cors8.append(vertex.tolist()[0])
                # print(vertex.tolist()[0])
                x, y = vertex[0]
                # cv2.circle(image, (x, y), 5, (255, 0, 0), -1)


        # print(approx)
        if len(approx) == 4:
            rectangles.append(approx)
        # 绘制矩形边框
    # for rectangle in rectangles:
        # print(rectangle)
        # cv2.drawContours(image, [rectangle], -1, (0, 255, 0), 2)

        # 计算矩形内外边框
        # x, y, w, h = cv2.boundingRect(rectangle)
        # cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

    
    # print(cors8)
    # print(cors8[2])
    if len(cors8) == 8:
        for i in range(len(cors8)):
            if i<4:
                if i==0 or i==2:
                    t=[]
                    t.append((cors8[i][0]+cors8[i+4][0])//2)
                    t.append((cors8[i][1]+cors8[i+4][1])//2)
                    cors4.append(t)
                else :
                    t=[]
                    t.append((cors8[i][0]+cors8[8-i][0])//2)
                    t.append((cors8[i][1]+cors8[8-i][1])//2)
                    cors4.append(t)


        print(cors4)

        for t in cors4:
            cv2.circle(image, (t[0], t[1]), 5, (255, 0, 0), -1)
        return cors4

    return []

    # 显示结果
    # cv2.imshow('Gray', edges)
    # cv2.imshow('Rectangles', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


    

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头。请检查是否连接了正确的摄像头设备。")
        return

    start_time = time.time()
    image_count = 0

    while True:
        ret, image = cap.read()
        print(image.shape)    # x 640 y 480
        
        image=image[120:400,230:500]  #[y1:y2,x1:x2]

        if not ret:
            print("无法获取视频帧。")
            break

        cors=drec(image)

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
