#!/usr/bin/env python

import lib
import time
from multiprocessing import Process, Manager

def main():
    # share client list across processes
    manager = Manager()
    streamers = manager.dict()
    receivers = manager.dict()

    # websocket server
    # server params
    WHOST = ''
    WPORT = 12345

    client_manager = lib.client_mng.ClientManager(streamers, receivers)
    server = lib.websocket_server.WebSocketServer(WHOST, WPORT, client_manager)

    # processes
    ps = []
    ps.append(Process(target=server.start_accept))
    ps.append(Process(target=server.monitor_clients))
    [p.start() for p in ps]
    [p.join() for p in ps]


if __name__ == '__main__':
    main()
