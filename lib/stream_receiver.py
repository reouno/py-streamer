import cv2
import numpy as np
import socket

class VideoStream():
    def __init__(self, socket_client):
        self.s = socket_client
        self.cam = self.frames()

    def get_frame(self):
        return next(self.cam)

    def frames(self):
        data = b''
        while True:
            packet = self.s.recv(buff_size=32768)
            if not packet:
                print('no more data received')
                self.s.close()
                exit()
            data += packet
            imgs_bytes = data.split(b'<--!END!-->')
            if len(imgs_bytes) > 1:
                for img_bytes in imgs_bytes[:-1]:
                    if img_bytes is None:
                        pass
                    else:
                        yield img_bytes
                data = imgs_bytes[-1]
            elif len(imgs_bytes) == 1:
                continue
            else:
                raise RuntimeError('invalid data: len(imgs_bytes) must be 1 or more.')
