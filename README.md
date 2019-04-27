# py-streamer
python video streaming server

# env

- test env: ubuntu18.04
- python3
- opencv3

# HOST and PORT setting

- set listening host and port in [server.py](https://github.com/reouno/py-streamer/blob/master/server.py)
- set server host and port in [streamer_client.py](https://github.com/reouno/py-streamer/blob/master/streamer_client.py), [streamer_client_raspi.py](https://github.com/reouno/py-streamer/blob/master/streamer_client_raspi.py), [receiver_client.py](https://github.com/reouno/py-streamer/blob/master/receiver_client.py)

# camera setting

- set resolution, fps, and device number in [streamer_client.py](https://github.com/reouno/py-streamer/blob/master/streamer_client.py) if you use webcam + opencv.
- set resolution in [streamer_client_raspi.py](https://github.com/reouno/py-streamer/blob/master/streamer_client_raspi.py) if you use raspberrypi + picamera module.

# How to run

```
# start websocket server
python server.py

# start streamer client
# if use opencv for capturing camera
python streamer_client.py
# if use picamera for capturing camera
python streamer_client_raspi.py

# start receiver client
# env that can open GUI server
python receiver_client.py
# cui env (just for debug)
python receiver_client.py --only-cui
```

# TODO
- [ ] set HOST and PORT in command line args
- [ ] appropriate termination
- [ ] selective connection between streamer and receiver
- [x] seperate streaming channels when a receiver receives videos from multiple streamers

## LICENCE

This software is released under the MIT License, see [LICENSE.txt](https://github.com/reouno/py-streamer/blob/master/LICENSE.txt).
