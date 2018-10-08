import cv2
import lib
import numpy as np
import socket
import time
from datetime import datetime


if __name__ == '__main__':
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument('--only-cui', help='check if receiver running in cui for debug use', action='store_true')
    a = psr.parse_args()
    # server params
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345

    soc = lib.websocket_client.WebSocketClient(SERVER_HOST, SERVER_PORT)
    print('connection success!')
    cam = lib.stream_receiver.VideoStream(soc)
    while 1:
        frame = cam.get_frame()
        img = cv2.imdecode(np.fromstring(frame, np.uint8),cv2.IMREAD_COLOR)
        if img is None:
            continue
        print(datetime.now(), img.shape)
        #print(len(img))
        if not a.only_cui:
            cv2.imshow("streaming", img)
            if cv2.waitKey(10) == ord('q'):
                break
    cv2.destroyAllWindows()
