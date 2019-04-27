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
            try:
                time.sleep(0.01)
                print('listen at {}:{}'.format(self.HOST, self.PORT))
                client_socket, addr = self.s.accept()
                client_id = str(uuid.uuid4())
                discriminator = client_socket.recv(1024)
                channel = discriminator[9:].decode('utf-8')
                # discriminator must be like b"streamer_somename"
                if discriminator.find(b'streamer_') == 0:
                    print('found streamer. channel is "{}"'.format(channel))
                    ret = self.client_manager.add_streamer(client_socket, addr, client_id, channel)
                    if not ret:
                        client_socket.send(b'channel_already_used')
                        continue
                    streamer = ThreadedStreamer(self, client_socket, addr, client_id, channel)
                    ps.append(Process(target = streamer.start_deliver))
                    ps[-1].start()
                    print('start streamer')
                elif discriminator.find(b'receiver_') == 0:
                    self.client_manager.add_receiver(client_socket, addr, client_id, channel)
                else:
                    raise RuntimeError('invalid connection protocol: initial data must be b"streamer" or b"receiver"')
                print('new client connected as "{}", addr:{}, id:{}, channel:{}'.format(discriminator.decode('utf-8'), addr, client_id, channel))
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                [p.terminate() for p in ps]
                self.s.close()
                break
        [p.join() for p in ps]

    def start_deliver(self, streamer, streamer_addr, streamer_id, channel):
        '''deliver video stream from streamer to receivers via this server'''
        try:
            while 1:
                if self.client_manager.len_receivers() == 0:
                    pass
                else:
                    if not self.__deliver__(streamer, streamer_addr, streamer_id, channel):
                        break
        except KeyboardInterrupt:
            print('exit process by KeyboardInterrupt')
            return

    def get_status(self, interval=1):
        '''you should use monitor_clients rather than this method.'''
        try:
            while 1:
                len_streamers, len_streamers = self.client_manager.get_status()
                print('num streamers: {}, num receivers: {}'.format(len_streamers, len_receivers))
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    def monitor_clients(self, interval=1):
        '''monitor all clients and delete if connection closed'''
        try:
            while 1:
                len_streamers, len_receivers = self.client_manager.monitor_clients()
                print('[{}]: num streamers: {}, num receivers: {}'.format(datetime.datetime.now(), len_streamers, len_receivers))
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    def __deliver__(self, streamer, streamer_addr, streamer_id, channel) -> bool:
        try:
            data = streamer.recv(32768)
        except (BrokenPipeError, ConnectionResetError):
            streamer.close()
            print('closed streamer connection {}, id:{}, channel:{}'.format(streamer_addr, streamer_id, channel))
            self.client_manager.delete_streamer(streamer_id)
            return False
        for client_id, (conn, addr, client_channel) in self.client_manager.receivers():
            if client_channel == channel:
                try:
                    conn.sendall(data)
                except (BrokenPipeError, ConnectionResetError):
                    conn.close()
                    print('closed receiver connection {}, id:{}, channel:{}'.format(addr, client_id, client_channel))
                    self.client_manager.delete_receiver(client_id)
        return True

class ThreadedStreamer(object):
    def __init__(self, websocket_server, streamer, streamer_addr, streamer_id, channel):
        self.server = websocket_server
        self.streamer = streamer
        self.streamer_addr = streamer_addr
        self.streamer_id = streamer_id
        self.channel = channel

    def start_deliver(self):
        self.server.start_deliver(self.streamer, self.streamer_addr, self.streamer_id, self.channel)
