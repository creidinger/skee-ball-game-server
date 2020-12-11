import sys
import logging
import socket
import _thread
import time
import json

from threader import ThreadedServer
from game_state import Game

# Basic setup
logging.basicConfig(filename="log/server.log", level=logging.DEBUG)

logging.info("================================\nserver.py: Socket Server Running\n==========================================")

# Main loop
# Always attempts socket connection


def run_game():
    """Initialize game and start loop"""

    logging.info('run_game(): Game Start')
    hostname = socket.gethostname()
    # IPAddr = socket.gethostbyname(hostname)

    while True:
        ThreadedServer('10.0.0.63', 5000).bind()
        time.sleep(3)
    # end main loop


run_game()
