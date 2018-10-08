#import cv2
import datetime
import io
import numpy as np
import picamera
import socket
import time

class Camera(object):
    def __init__(self):
        self.RESOLUTION = (640, 480)
        self.cam = self.frames()

    def frames(self):
        with picamera.PiCamera() as camera:
            camera.resolution = self.RESOLUTION
            time.sleep(2) # let camera warm up

            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream,
                                                'jpeg',
                                                use_video_port=True):
                stream.seek(0) # return current stream
                yield stream.read()
                #img_bytes = stream.read()
                #img = cv2.imdecode(np.fromstring(img_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                #print(img.shape)
                #yield img_bytes



                stream.seek(0) # reset stream for next frame
                stream.truncate()

    def get_frame(self):
        return next(self.cam)

if __name__ == '__main__':
    # server params
    SERVER_HOST = '192.168.0.2'
    SERVER_PORT = 12345

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.connect((SERVER_HOST, SERVER_PORT))
    soc.send(b'streamer')

    camera = Camera()
    try:
        while 1:
            img = camera.get_frame()
            soc.sendall(img)
            soc.send(b'<--!END!-->')
            print(datetime.datetime.now(), len(img))
    except KeyboardInterrupt:
        print('close streaming')

