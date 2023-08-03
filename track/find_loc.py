import cv2
import time
R=1


def floc(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 查找图像中最亮点的敏感方法是使用cv2.minMaxLoc，称其敏感的原因是该方法极易受噪音干扰，可以通过预处理步骤应用高斯模糊解决。
        # 寻找最小、最大像素强度所在的（x,y）
    (minVal, maxVal, minLoc, center) = cv2.minMaxLoc(gray)
        # 在最大像素上绘制空心蓝色圆圈
    # cv2.circle(frame, center, 5, (255, 0, 0), 2)

        # 展示该方法的结果
    # cv2.imshow("Naive", frame)
    return center

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头。请检查是否连接了正确的摄像头设备。")
        return

    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("无法获取视频帧。")
            break


        orig = frame.copy()

        center=find_loc(frame)
        # 在最大像素上绘制空心蓝色圆圈
        if center:
            cv2.circle(frame, center, 5, (255, 0, 0), 2)

            # 展示该方法的结果
            cv2.imshow("Naive", frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 使用cv2.minMaxLoc，如果不进行任何预处理，可能会非常容易受到噪音干扰。
        # 相反，最好先对图像应用高斯模糊以去除高频噪声。这样，即使像素值非常大（同样由于噪声）也将被其邻居平均。
        # 在图像上应用高斯模糊消除高频噪声，然后寻找最亮的像素
        # 高斯模糊的半径取决于实际应用和要解决的问题；
        gray = cv2.GaussianBlur(gray, (R, R), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        frame = orig.copy()
        cv2.circle(frame, maxLoc, R, (255, 0, 0), 2)


        frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - start_time
        fps = frame_count / elapsed_time

        # 在视频帧上绘制帧率信息
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Video", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
