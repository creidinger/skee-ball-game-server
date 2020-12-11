import logging
import json
import threading

import server_functions as sf
from settings import Settings


class Player():
    """Handles player position and state"""

    def __init__(self):
        """Init emply player with required settings"""
        self.id = None
        self.name = None
        self.score = 0              # Running sum of players score
        self.state = "inactive"
        # leaderboard
        self.score_reached = False
        self.time = 0               # time sent to leaderboard

    def update(self, data, lap_time):
        """update player state based on incomming data"""
        # convert to string to json object
        # see conversions if you're having problems
        # https://docs.python.org/3/library/json.html#encoders-and-decoders
        try:
            data = json.loads(data)

            if data['state'] == 'inactive':
                self.player_reset()

            # updated player state
            self.id = data['id']
            self.name = data['name']
            self.score = self.score + data['score']
            self.state = data['state']

            self.check_winner(self.score, lap_time)

        except Exception as e:
            logging.error(
                "Player.update() Unable to update player data. \n{}\nData Received from player id: {}: {}".format(str(e), self.id, data))

    def check_winner(self, score, lap_time):
        """Check to see if the player has reached 100"""

        # if the score is reached set to true and store the time
        # game_state.py will update and handle leaderboard once the score_reached flag is true
        if score >= 100:
            self.score_reached = True
            self.time = lap_time

    def player_reset(self):
        """Reset the palyer data to ensure no data carries over between rounds"""

        logging.info(
            "Player.player_reset(): Player {} score and time reset".format(self.id))
        self.id = None
        self.name = None
        self.score = 0
        self.state = "inactive"
        self.score_reached = False
        self.time = 0
