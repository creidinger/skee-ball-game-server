# Main socket client that sends player data to Server
# Author: Chase Reidinger

import socket
import threading
import time
import logging
import json

logging.basicConfig(filename="log/client.log", level=logging.DEBUG)


def connect_to_server(server, port):
    """Keep trying to connect to socket server.py"""

    connected = False

    while not connected:
        try:
            logging.info(
                "connect_to_server(): Connecting to {}:{}".format(server, str(port)))
            logging.info("==========" * 7)
            s.connect((server, port))

            data = '''Handshake<EOF>'''

            # send conneciton confirmation
            try:
                s.send(str.encode(data))
                response = s.recv(2048).decode()
                logging.info(
                    "connect_to_server(): Server Response: {}".format(response))

                if response == '''{"connected": "True"}''':
                    connected = True

            except socket.error as e:
                logging.error("connect_to_server(): {}\n".format(str(e)))
                time.sleep(2)

        except socket.error as e:
            logging.error("connect_to_server(): {}\n".format(str(e)))
            time.sleep(2)
# End connect_to_server()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    hostname = socket.gethostname()
    # IPAddr = socket.gethostbyname(hostname)
    connect_to_server('10.0.0.63', 5000)

    # # Sample wall request
    # data = '''WallRequest<EOF>'''
    # s.send(str.encode(data))
    #
    # data = s.recv(2048).decode()
    # logging.info("client: Server Response: {}".format(data))

    # Sample client request
    # initial msg
    data = '''{"id": 1, "name":"X000Z43GLR", "score":0, "state": "lobby"}<EOF>'''

    time.sleep(4)

    i = 0

    # Main loop
    while True:

        try:
            # data = '''DataRequest<EOF>'''
            data = '''for_valhalla<EOF>'''
            # data = '''{"id": 1, "name":"X000Z43GLR", "score": 20, "state": "lobby"}<EOF>'''
            # msg = json.dumps(str(json_obj))
            s.send(str.encode(data))
            # logging.info("socket(): data sent to server...")

            i = i + 20
            time.sleep(1)

            if i is 100:
                i = 0
                data = '''{"id": 1, "name":"X000Z43GLR", "score":0, "state": "inactive"}<EOF>'''
                s.send(str.encode(data))
                time.sleep(5)
                data = '''{"id": 1, "name":"X000Z43GLR", "score":0, "state": "lobby"}<EOF>'''
                s.send(str.encode(data))
                time.sleep(4)

        except socket.error as e:
            logging.error(
                "ThreadedServer.listen_to_client(): Unable to send data to server")
            logging.error(
                "ThreadedServer.listen_to_client(): {}".format(str(e)))

        try:
            # Receive data from server
            data = s.recv(2048).decode()
            logging.info("client: Server Response: {}".format(data))

        except socket.error as e:
            logging.error(
                "ThreadedServer.listen_to_client(): Unable to recevie server data...")
            logging.error(
                "ThreadedServer.listen_to_client(): {}".format(str(e)))
            # client.close()

        time.sleep(.25)

    # end while
