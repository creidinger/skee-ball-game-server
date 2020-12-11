import socket
import threading
import logging
import time
import json

from game_state import Game
from player import Player
import server_functions as sf


class ThreadedServer():
    """Socket server that received client connections and data"""

    def __init__(self, host, port):
        """Init the threaded server settings"""
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = None
        self.server_comm_pause_start = 0
        self.game = Game()
        # self.send_comm = False

    def bind(self):
        """Bind IP address and Port for the server"""
        try:
            logging.info(
                'ThreadedServer.bind(): Try to create socket on {}:{}'.format(self.host, self.port))
            self.sock.bind((self.host, self.port))

        except socket.error as e:
            logging.error('ThreadedServer.bind(): {}'.format(str(e)))

        else:
            logging.info(
                'ThreadedServer.bind(): Socket created on {}.{}'.format(self.host, self.port))
            logging.info("==========" * 7)

            self.listen()

    def listen(self):
        """
        Listen for new connections to the server
        and start a new thread for each new connection
        """
        logging.info(
            "ThreadedServer.listen(): listening for new client connection...")
        self.sock.listen(5)

        while True:
            client, address = self.sock.accept()
            self.client = client
            # client.settimeout(10)
            logging.info(
                "================================================================\nThreadedServer.listen(): Connected to: {}:{}\n==========================================================================".format(address[0], str(address[1])))
            threading.Thread(target=self.listen_to_client,
                             args=(client, address, Player())).start()
            logging.info(
                "ThreadedServer.listen() Show active threads \n{}".format(threading.enumerate()))

    def listen_to_client(self, client, address, player):
        """Listen for data being sent from the client"""

        # Client/server Communication loop
        while True:

            try:
                # receive data and decode data,
                # then pass to the player class if data is not empty.
                data = client.recv(8192).decode()

            except socket.error as e:
                logging.error(
                    "ThreadedServer.listen_to_client(): Unable to recevie client data... closing client connection \n{}".format(str(e)))
                client.close()
                return False

            else:
                # no data received
                if data == "":
                    continue

                else:
                    # always clean incomming data
                    data = sf.clean_json_data(data)

                    # connection confirmation
                    if data == "Handshake":
                        try:
                            response = '''{"connected": "True"}'''
                            client.send(str.encode(response))
                            logging.info(
                                "ThreadedServer.listen_to_client(): connection confirmation sent...\n")
                            continue

                        except socket.error as e:
                            logging.error(
                                "ThreadedServer.listen_to_client(): Unable to send connection confirmation... closing client connection \n{}".format(str(e)))
                            client.close()

                    # heartbeat data request for wall and ipads when in lobby
                    elif data == "DataRequest":
                        # logging.info(
                        #     "ThreadedServer.listen_to_client(): {}\n".format(data))
                        client.send(str.encode(self.game.send_game_state()))
                        continue
                    # Current Player stats sent to wall
                    elif data == "WallRequest":
                            # logging.info(
                            #     "ThreadedServer.listen_to_client(): {}\n".format(data))
                        client.send(str.encode(self.game.send_wall_data()))
                        continue
                    # Top 5 players to wall
                    elif data == "Leaderboard":
                        # logging.info(
                        #     "ThreadedServer.listen_to_client(): {}\n".format(data))
                        client.send(str.encode(self.game.send_leaderboard()))
                        continue
                    # Master reset of the game
                    # Torch everything... No survivors, only glory
                    elif data == "for_valhalla":
                        logging.info(
                            "ThreadedServer.listen_to_client(): {}\n".format(data))
                        self.game.reset_game()
                        continue
                    else:
                        # logging.info(
                        #     "ThreadedServer.listen_to_client(): {}\n".format(data))
                        player.update(data, self.game.lap_time_durration)
                        self.game.update_player_data(player)
                        client.send(str.encode(self.game.send_game_state()))
