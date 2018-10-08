import datetime
import socket
import uuid
import time
from .client_mng import ClientManager
from multiprocessing import Process

class WebSocketServer(object):
    def __init__(self, host, port, client_manager, max_num_wait=5):
        self.HOST = host
        self.PORT = port
        self.max_num_wait = max_num_wait
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(self.max_num_wait)
        self.client_manager = client_manager

    def start_accept(self):
        '''register new clients and start deliver if streamer'''
        ps = []
        while 1:
            time.sleep(0.01)
            try:
                print('listen at {}:{}'.format(self.HOST, self.PORT))
                client_socket, addr = self.s.accept()
                client_id = str(uuid.uuid4())
                discriminator = client_socket.recv(1024)
                if discriminator == b'streamer':
                    print('found streamer')
                    self.client_manager.add_streamer(client_socket, addr, client_id)
                    streamer = ThreadedStreamer(self, client_socket, addr, client_id)
                    ps.append(Process(target = streamer.start_deliver))
                    ps[-1].start()
                    print('start streamer')
                elif discriminator == b'receiver':
                    self.client_manager.add_receiver(client_socket, addr, client_id)
                else:
                    raise RuntimeError('invalid connection protocol: initial data must be b"streamer" or b"receiver"')
                print('new client connected as "{}", addr:{}, id:{}'.format(discriminator.decode('utf-8'), addr, client_id))
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.s.close()
        [p.join() for p in ps]

    def start_deliver(self, streamer, streamer_addr, streamer_id):
        '''deliver video stream from streamer to receivers via this server'''
        try:
            while 1:
                if self.client_manager.len_receivers() == 0:
                    pass
                else:
                    if not self.__deliver__(streamer, streamer_addr, streamer_id):
                        break
        except KeyboardInterrupt:
            print('exit process by KeyboardInterrupt')
            return

    def get_status(self):
        try:
            while 1:
                len_streamers, len_streamers = self.client_manager.get_status()
                print('num streamers: {}, num receivers: {}'.format(len_streamers, len_receivers))
                time.sleep(5)
        except KeyboardInterrupt:
            pass

    def monitor_clients(self):
        '''monitor all clients and delete if connection closed'''
        while 1:
            len_streamers, len_receivers = self.client_manager.monitor_clients()
            print('num streamers: {}, num receivers: {}'.format(len_streamers, len_receivers))
            time.sleep(1)

    def __deliver__(self, streamer, streamer_addr, streamer_id) -> bool:
        try:
            data = streamer.recv(32768)
        except (BrokenPipeError, ConnectionResetError):
            streamer.close()
            print('closed streamer connection {}, id:{}'.format(streamer_addr, streamer_id))
            self.client_manager.delete_streamer(streamer_id)
            return False
        for client_id, (conn, addr) in self.client_manager.receivers():
            try:
                conn.sendall(data)
            except (BrokenPipeError, ConnectionResetError):
                conn.close()
                print('closed receiver connection {}, id:{}'.format(addr, client_id))
                self.client_manager.delete_receiver(client_id)
        return True

class ThreadedStreamer(object):
    def __init__(self, websocket_server, streamer, streamer_addr, streamer_id):
        self.server = websocket_server
        self.streamer = streamer
        self.streamer_addr = streamer_addr
        self.streamer_id = streamer_id

    def start_deliver(self):
        self.server.start_deliver(self.streamer, self.streamer_addr, self.streamer_id)
