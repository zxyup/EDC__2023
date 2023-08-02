# Blob Detection Example
#
# This example shows off how to use the find_blobs function to find color
# blobs in the image. This example in particular looks for dark green objects.
import sensor, image, time,pyb,lcd
import ustruct
import array
from pyb import UART
from pid import PID
RED_LED_PIN = 1
BLUE_LED_PIN = 3
# You may need to tweak the above settings for tracking green things...
# Select an area in the Framebuffer to copy the color settings.
uart = UART(3, 9600,timeout_char=3000)
sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

# For color tracking to work really well you should ideally be in a very, very,
# very, controlled enviroment where the lighting is constant...
red_threshold  = (13, 49, 18, 64, 121, -98)
size_threshold = 2000
x_pid = PID(p=0.5, i=1, imax=100)
h_pid = PID(p=0.05, i=0.1, imax=50)
pan_pid = PID(p=0.1, i=0, imax=90)#在线调试使用这个PID

def find_max(blobs):
    max_size=0
    for blob in blobs:
        if blob[2]*blob[3] > max_size:
            max_blob=blob
            max_size = blob[2]*blob[3]
    return max_blob
def sending_data(cx,cy,cw,ch):
    global uart;
    data = ustruct.pack("<hhhh",
                   int (cx),
                   int (cy),
                   int (cw),
                   int (ch),
                   )
    uart.write(data);   #必须要传入一个字节数组
while(True):
    clock.tick() # Track elapsed milliseconds between snapshots().
    img = sensor.snapshot() # Take a picture and return the image.
    pyb.LED(BLUE_LED_PIN).on()
    blobs = img.find_blobs([red_threshold])
    if blobs:
        max_blob = find_max(blobs)
        pan_error = max_blob.cx()-img.width()/2#等价x_error
        x_error = max_blob[5]-img.width()/2
        h_error = max_blob[2]*max_blob[3]-size_threshold
        for b in blobs:
            # Draw a rect around the blob.
            img.draw_rectangle(b[0:4]) # rect
            img.draw_cross(b[5], b[6]) # cx, cy

        img.draw_rectangle(max_blob[0:4]) # rect
        img.draw_cross(max_blob[5], max_blob[6]) # cx, cy
        pan_output=pan_pid.get_pid(pan_error,1)/2
        x_output=x_pid.get_pid(x_error,1)
        h_output=h_pid.get_pid(h_error,1)
        x=(int)(x_output+1000)
        h=(int)(h_output+1000)
        cx=(int)(pan_output*10)
        x1=int(x/10)
        x2=(int)(x%10)
        h1=(int)(h/10)
        h2=int(h%10)
        #print("x_output",x_output)
        #print("h_output",h_output)
        print(cx)
        FH=bytearray([0x2C,0x12,cx,x1,x2,h1,h2,0x5B])
        uart.write(FH)
    else:
        FH=bytearray([0x2C,0x12,0,0,0,0,0,0x5B])
        uart.write(FH)



