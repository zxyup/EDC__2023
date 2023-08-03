import cv2
import numpy as np

def fbb(image):
    # 转换为灰度图像
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 对图像进行二值化处理
    _, thresholded = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)

    # 寻找轮廓
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 找到最大的轮廓（黑色块）
    print(len(contours))
    if contours:
        # max_contour = max(contours, key=cv2.contourArea)
        for contour in contours:
            

            # 计算最大轮廓的矩形边界框
            x, y, w, h = cv2.boundingRect(contour)

            
            # 计算黑色块的中心点坐标
            center_x = x + w // 2
            center_y = y + h // 2

            # cv2.circle(image, (center_x, center_y), 5, (0, 0, 255), -1)  # 在中心点处画一个红色的圆

        # cv2.imshow('1',image)


        return center_x, center_y

    return None

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
        center = find_black_blob_center(frame)

        # if center:
        #     center_x, center_y = center
        #     cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # 在中心点处画一个红色的圆

        # cv2.imshow("Black Blob Center Detection", frame)

        # 按 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
