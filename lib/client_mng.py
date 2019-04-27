#!/usr/bin/env python

'''
- manage receiver and streamer
- add, delete
- len
- get_status


- discriminate, monitor
- select and create connection between streamer and receivers
'''

import datetime

class ClientManager(object):
    def __init__(self, shared_streamers, shared_receivers, shared_channels):
        self.shared_streamers = shared_streamers
        self.shared_receivers = shared_receivers

    def streamers(self):
        return self.shared_streamers.items()

    def receivers(self):
        return self.shared_receivers.items()

    def channels(self):
        return [c for _, _, c in self.shared_streamers.values()]

    def add_streamer(self, streamer, addr, streamer_id, channel) -> bool:
        if (streamer_id in self.shared_streamers) or (channel in self.channels()):
            print('streamer already exists, addr:{}, id:{}, channel:{}'.format(addr, streamer_id, channel))
            return False
        else:
            self.shared_streamers[streamer_id] = (streamer, addr, channel)
            return True

    def add_receiver(self, receiver, addr, receiver_id, channel) -> bool:
        if receiver_id in self.shared_receivers:
            print('receiver already exists, addr:{}, id:{}, channel:{}'.format(addr, receiver_id, channel))
            return False
        else:
            self.shared_receivers[receiver_id] = (receiver, addr, channel)
            return True

    def delete_streamer(self, streamer_id) -> bool:
        if streamer_id in self.shared_streamers:
            del self.shared_streamers[streamer_id]
            return True
        else:
            print('streamer not exists, id:{}'.format(streamer_id))
            return False

    def delete_receiver(self, receiver_id) -> bool:
        if receiver_id in self.shared_receivers:
            del self.shared_receivers[receiver_id]
            return True
        else:
            print('receiver not exists, id:{}'.format(receiver_id))
            return False

    def len_streamers(self) -> int:
        return len(self.shared_streamers)

    def len_receivers(self) -> int:
        return len(self.shared_receivers)


    # utility methods

    def get_status(self) -> (int, int):
        '''return each no. of streamers and receivers those are registered'''
        return self.len_streamers(), self.len_receivers()

    def monitor_clients(self) -> (int, int):
        '''return each no. of streamers and receivers those are alive'''
        return self.__monitor_streamers__(), self.__monitor_receivers__()

    def __monitor_streamers__(self) -> int:
        '''monitor streamers and delete if connection closed'''
        for streamer_id, (conn, addr, channel) in self.shared_streamers.items():
            try:
                conn.send(str(datetime.datetime.now()).encode('utf-8') + b'Hey, you alive?')
            except (BrokenPipeError, ConnectionResetError):
                conn.close()
                print('closed streamer connection {}, id:{}, channel:{}'.format(addr, streamer_id, channel))
                self.delete_streamer(streamer_id)
        return self.len_streamers()

    def __monitor_receivers__(self) -> int:
        '''monitor receivers and delete if connection closed'''
        for receiver_id, (conn, addr, channel) in self.shared_receivers.items():
            try:
                conn.send(str(datetime.datetime.now()).encode('utf-8') + b'Hey, you alive?')
            except (BrokenPipeError, ConnectionResetError):
                conn.close()
                print('closed receiver connection {}, id:{}, channel:{}'.format(addr, receiver_id, channel))
                self.delete_receiver(receiver_id)
        return self.len_receivers()
