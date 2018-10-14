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
    psr.add_argument('-s', '--save-video-file', help='path to save video. not save video in default. this param will be ignored if --only-cui is used.', default='')
    a = psr.parse_args()
    # server params
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345

    soc = lib.websocket_client.WebSocketClient(SERVER_HOST, SERVER_PORT)
    print('connection success!')
    cam = lib.stream_receiver.VideoStream(soc)

    # for video saving
    save_video = len(a.save_video_file) > 0
    if save_video:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(a.save_video_file, fourcc, 24.0, (640, 480))
    while 1:
        frame = cam.get_frame()
        img = cv2.imdecode(np.fromstring(frame, np.uint8),cv2.IMREAD_COLOR)
        if img is None:
            continue
        print(datetime.now(), img.shape)
        #print(len(img))
        if not a.only_cui:
            cv2.imshow("streaming", img)
            if save_video:
                out.write(img)
                print('saved frame')
            if cv2.waitKey(10) == ord('q'):
                break
    if not a.only_cui:
        if save_video:
            out.release()
        cv2.destroyAllWindows()
