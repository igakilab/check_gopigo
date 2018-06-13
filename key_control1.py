import easygopigo3

import cv2
import picamera
import picamera.array
import time
############################################################
class gopigo_control:
    # Init various camera parameter.
    # Finally, every parameter should be fixed to reasonable values.
    def __init__(self):
        self.width = 640
        self.height = 480
        self.camera = picamera.PiCamera(resolution=(self.width,self.height),framerate=10)
        self.camera.iso = 100
        # Wait for the automatic gain control to settle
        time.sleep(2)
        # Fix the values
        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'
        g = self.camera.awb_gains
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g
        print("shutter:"+str(self.camera.shutter_speed)+" awb_gains:"+str(g))

    # capture a frame from picamera
    def capture_frame(self):
        cap_stream = picamera.array.PiRGBArray(self.camera,size=(self.width,self.height))
        self.camera.capture(cap_stream, format='bgr',use_video_port=True)
        frame = cap_stream.array
        return frame

###########################################################



gpgc = gopigo_control()
egpi = easygopigo3.EasyGoPiGo3()
egpi.set_speed(500)

n = 0

while True:
    frame = gpgc.capture_frame()
    cv2.imshow("Camera",frame)

    w = cv2.waitKey(1) % 256

    if w==ord('w'):
        egpi.forward()
    elif w==ord('d'):
        egpi.right()
    elif w==ord('a'):
        egpi.left()
    elif w==ord('s'):
        egpi.backward()
    elif w==ord('x'):
        egpi.stop()
    elif w==ord('p'):
        egpi.stop()
        break
    elif w == ord('1'):
        cv2.imwrite('/home/pi/ipbl/imgdir/files{0}.jpg'.format(n),frame)
        n = n + 1
    


