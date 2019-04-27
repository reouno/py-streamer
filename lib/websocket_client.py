import socket

class WebSocketClient():
    '''WebSocket client
    - set server host/port when initialization
    - automatically connect to server when initialization
    - can send data and recv
    - receiving buffer size is recommended to relatively small exponent of 2 such as 4096.
    - should the connection close at the end'''

    def __init__(self, host, port, stream_name):
        self.SERVER_HOST = host
        self.SERVER_PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connect__()
        self.send(b'receiver_' + stream_name.encode('utf-8'))

    def __connect__(self):
        self.s.connect((self.SERVER_HOST, self.SERVER_PORT))

    def recv(self, buff_size=4096):
        return self.s.recv(buff_size)

    def send(self, buf):
        self.s.sendall(buf)

    def close(self):
        self.s.close()
