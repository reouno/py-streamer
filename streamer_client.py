import cv2
import datetime
import socket
import time

def videoCapture(resolution=(640,480), fps=24, device=0):
    cap = cv2.VideoCapture(device)
    cap.set(3, resolution[0])
    cap.set(4, resolution[1])
    cap.set(5, fps)
    return cap

def encode_to_string(img, img_format='.jpg'):
    '''encode uint8 image to byte string'''
    return cv2.imencode(img_format, img)[1].tobytes()

if __name__ == '__main__':
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument('--name', help='streaming name (id)', default='anonymous')
    a = psr.parse_args()

    # websocket server
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345

    # camera params
    RESOLUTION = 640, 480
    FPS = 15
    DEVICE = 0

    cam = videoCapture(resolution=RESOLUTION, fps=FPS, device = DEVICE)

    try:
        while 1:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                soc.connect((SERVER_HOST, SERVER_PORT))
                soc.send(b'streamer_' + a.name.encode('utf-8'))
                if soc.recv(100).find(b'channel_already_used') == 0:
                    print('channel "{}" is already used.'.format(a.name))
                    exit()
                while True:
                    ret_val, img = cam.read()
                    img_bytes = encode_to_string(img)
                    print(len(img_bytes))
                    soc.sendall(img_bytes)
                    soc.send(b'<--!END!-->')
            except ConnectionResetError as e:
                print(datetime.datetime.now(), e)
                soc.close()
                time.sleep(2)
                continue
            except ConnectionRefusedError as e:
                print(datetime.datetime.now(), e)
                soc.close()
                time.sleep(10)
                continue
    except KeyboardInterrupt:
        pass
    finally:
        print('close socket')
        soc.close()
        cam.release()
