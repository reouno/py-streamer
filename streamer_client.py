import cv2
import redis
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
    # websocket server
    SERVER_HOST = 'localhost'
    SERVER_PORT = 12345

    # camera params
    RESOLUTION = 640, 480
    FPS = 24
    DEVICE = 0

    cam = videoCapture(resolution=RESOLUTION, fps=FPS, device = DEVICE)

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.connect((SERVER_HOST, SERVER_PORT))
    soc.send(b'streamer')
    try:
        while 1:
            try:
                while True:
                    ret_val, img = cam.read()
                    img_bytes = encode_to_string(img)
                    print(len(img_bytes))
                    soc.sendall(img_bytes)
                    soc.send(b'<--!END!-->')
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        pass
    finally:
        print('close socket')
        soc.close()
