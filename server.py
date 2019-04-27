#!/usr/bin/env python

import lib
import time
from multiprocessing import Process, Manager

def main():
    # share client list across processes
    manager = Manager()
    streamers = manager.dict()
    receivers = manager.dict()
    channels = manager.dict()

    # websocket server
    # server params
    WHOST = ''
    WPORT = 12345

    client_manager = lib.client_mng.ClientManager(streamers, receivers, channels)
    server = lib.websocket_server.WebSocketServer(WHOST, WPORT, client_manager)

    # processes
    ps = []
    ps.append(Process(target=server.start_accept))
    ps.append(Process(target=server.monitor_clients))
    [p.start() for p in ps]
    try:
        while 1:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print('stop all process...')
    [p.join() for p in ps]


if __name__ == '__main__':
    main()
