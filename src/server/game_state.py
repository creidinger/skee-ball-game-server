import logging
import json
import time
import csv
import operator


class Game():
    """module that handls game status and user positions"""

    def __init__(self):
        """init settings for game"""
        # SETTINGS
        self.lap_time_durration = 0         # time elapsed during a race
        self.lap_time_start = 0             # current time when a race starts
        self.round_over = False
        self.game_state = {}                # return value of the overall game sent to clients
        self.game_winner_id = None
        self.game_winner_time = None
        self.master_reset = False
        self.master_reset_start = 0
        self.logger_pause_start = 0         # Used to updated the log file
        # LOBBY
        self.game_status = "in_lobby"       # indicates if we're playing or not
        self.countdown_start = 0
        self.countdown_duration = 10
        self.countdown_remaining = self.countdown_duration
        # player state counters
        self.players_inactive = None
        self.players_in_lobby = None
        self.players_countdown = None
        self.players_in_race = None

        # PLAYERS
        # Ensure no None values
        # None/Null are not being handled on the client side
        self.player_one = {"id": 1, "state": "inactive",
                           "name": "Player 1", "score": 0, "score_reached": False, "time": 0}
        self.player_two = {"id": 2, "state": "inactive",
                           "name": "Player 1", "score": 0, "score_reached": False, "time": 0}
        self.player_three = {"id": 3, "state": "inactive",
                             "name": "Player 1", "score": 0, "score_reached": False, "time": 0}

        self.players = [self.player_one, self.player_two,
                        self.player_three]

    def update_player_data(self, player):
        """updated the player state for each player ID"""

        # this is called by threader.py
        # the Player object is init with each thread
        try:
            # iterate the list of players
            # check agains the ID received form the thread
            for p in self.players:

                # logging.info("Game.update_player_data(): {}".format(player.__dict__))
                # Dump all player attributes and prep for return to each endpoint
                if player.id == 1:
                    self.player_one = player.__dict__
                elif player.id == 2:
                    self.player_two = player.__dict__
                elif player.id == 3:
                    self.player_three = player.__dict__

                # update playerers into a list of dictionaries
                # This allows us to nicely drop the players into a json string on return to end points
                self.players = [self.player_one, self.player_two,
                                self.player_three]
        except Exception as e:
            logging.error(
                "Game.update_player_data(): Unable to update player data \n{}".format(str(e)))

    def check_client_player_states(self):
        """toggles the flags for game in play"""

        # possible player states
        self.players_inactive = 0
        self.players_in_lobby = 0
        self.players_countdown = 0
        self.players_in_race = 0

        try:

            # Tally each player state
            for p in self.players:
                # logging.info('Game.check_client_player_states(): p {}'.format(p))
                if p["state"] == "inactive":
                    self.players_inactive += 1
                elif p["state"] == "lobby":
                    self.players_in_lobby += 1
                elif p["state"] == "countdown":
                    self.players_countdown += 1
                elif p["state"] == "in_race":
                    self.players_in_race += 1

        except Exception as e:
            logging.error(
                "Game.check_client_player_states(): Unable to update player state \n{}".format(str(e)))

    def check_server_game_status(self):
        """See if players are joining lobby"""

        # Server is either in_lobby or in_race

        # logging.info('Game.check_server_game_status(): players_in_lobby {}'.format(
        #     self.players_in_lobby))

        if self.game_status == "in_race":
            self.update_lap_time()
            self.check_score_reached()

        elif self.players_in_lobby == 3:
            # players have joined and waiting to start
            self.round_over = False
            self.round_start_countdown()

        else:
            self.game_status = "in_lobby"

    def round_start_countdown(self):
        """Countdown to start a round"""

        # set start countdown time
        if self.countdown_start == 0:
            self.countdown_start = time.time()
            logging.info("Game.round_start_countdown(): Countdown starting")

        # countdown running
        elif self.countdown_start > 0 and self.countdown_remaining > 0:
            elapsed = time.time() - self.countdown_start
            self.countdown_remaining = self.countdown_duration - elapsed
            self.game_status = "in_lobby"
            # reset winner
            self.game_winner_id = None
            self.game_winner_time = None
            # logging.info('Game.round_start_countdown(): Countdown remaining {}\n'.format(
            #     self.countdown_remaining))

        # countdown over
        elif self.countdown_remaining <= 0:
            self.countdown_start = 0
            self.countdown_remaining = -1
            self.lap_time_start = time.time()
            self.game_status = "in_race"

    def update_lap_time(self):
        """increase the lap time while in race"""

        # logging.info("Game.update_lap_time(): {}".format(
        #     self.lap_time_durration))
        self.lap_time_durration = time.time() - self.lap_time_start

    def check_score_reached(self):
        """
        If a winner is found
         - set self.game_status to lobby
         - update leaderboard
        """

        try:
            # return to lobby if score is reached for any player
            for p in self.players:
                if p["score_reached"] is True:
                    self.round_over = True
                    self.game_status = "in_lobby"

                else:
                    continue

            if self.round_over is True:
                logging.info(
                    "Game.check_score_reached(): Winner found, ending round...")
                # reset the countdown before the next round
                self.countdown_remaining = self.countdown_duration
                self.lap_time_durration = 0
                self.lap_time_start = 0
                self.find_best_lap_time()

        except Exception as e:
            logging.error(
                "Game.check_score_reached(): There was a problem looking for a winner.\n{}".format(str(e)))

    def find_best_lap_time(self):
        """Loop through the list of players to find a winner"""

        current_winner = ''     # winner name
        self.game_winner_time = 0        # best time
        result = ''             # data being appended to .csv file

        try:
            # Look for the fastest laptime
            for p in self.players:
                # logging.info("Game.find_best_lap_time(): p {}".format(p))
                if p["score_reached"] is True:
                    if p["time"] > 0 and p["time"] > self.game_winner_time:
                        # updated current winnder
                        self.game_winner_id = p["id"]
                        current_winner = p["name"]
                        self.game_winner_time = p["time"]

            logging.info(
                "Game.find_best_lap_time(): \nWinner: {}\nBest time:{}".format(current_winner, self.game_winner_time))

            # construct the result to be stored in the .csv file
            result = {'name': current_winner, 'time': self.game_winner_time}
            self.update_leaderboard(result)

        except Exception as e:
            logging.error(
                "Game.find_best_lap_time(): There was a problem finding a winner.\n{}".format(str(e)))

    def update_leaderboard(self, result):
        """
        Update the leaderboard with the winner data
        Storeing results in a csv, the wall can sort it
        """

        logging.info("Game.update_leaderboard(): Checking best time")

        csv_file = 'assets/leaderboard.csv'

        try:
            # open csv file in append mode otherwise all data will be overwritten
            with open(csv_file, 'a') as f:
                csv_writer = csv.DictWriter(f, fieldnames=result)
                # write the result to a new row
                csv_writer.writerow(result)

            logging.info(
                "Game.update_leaderboard(): leaderboard updated\n")

        except Exception as e:
            logging.error(
                "Game.update_leaderboard(): Unabe to append survey results to survey.csv\n{}".format(str(e)))

    def send_wall_data(self):
        """Gather wall data into json object and return"""

        try:
            players_json = json.dumps(self.players)
            return players_json

        except Exception as e:
            logging.error(
                "Game.send_wall_data(): There was a problem sending player data to the wall.\n{}".format(str(e)))

    def send_leaderboard(self):
        """Send top 5 players to the wall as a json array"""

        csv_file = 'assets/leaderboard.csv'
        top_5_json = []

        try:
            # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
            # https://docs.python.org/3/howto/sorting.html
            with open(csv_file) as f:
                reader = csv.DictReader(f)
                # get an array of times and sort
                # then get the top 5 best times
                arr_time = [float(row['time']) for row in reader]
                arr_time.sort()
                top_5_time = [arr_time[r] for r in range(5)]

                i = 1
                for t in top_5_time:
                    # reset csv reader postion to top
                    f.seek(0)
                    for row in reader:
                        if row['time'] != 'time' and float(row['time']) == t:
                            top_5_json.append(
                                {"placement": i, "name": row['name'], "time": t})
                            i += 1

                # logging.info(
                #     f"Game.send_leaderboard(): top 5 {json.dumps(top_5_json, indent=4)}")

            return json.dumps(top_5_json)

        except Exception as e:
            logging.error(
                "Game.send_leaderboard() Unnable to send leaderboard to wall.\n{}".format(str(e)))

    def reset_game(self):
        """End game, erase all player data and send back to lobby"""

        try:
            # SETTINGS
            self.lap_time_durration = 0         # time elapsed during a race
            self.lap_time_start = 0             # current time when a race starts
            self.round_over = True
            self.game_winner_id = None
            self.game_winner_time = None
            self.master_reset = True
            # LOBBY
            self.game_status = "in_lobby"      # indicates if we're playing or not
            self.countdown_start = 0
            self.countdown_remaining = self.countdown_duration
            # player state counters
            self.players_inactive = 3

            self.player_one = {"id": 1, "state": "inactive",
                               "name": "Player 1", "score": 0, "score_reached": False, "time": 0}
            self.player_two = {"id": 2, "state": "inactive",
                               "name": "Player 1", "score": 0, "score_reached": False, "time": 0}
            self.player_three = {"id": 3, "state": "inactive",
                                 "name": "Player 1", "score": 0, "score_reached": False, "time": 0}

            self.players = [self.player_one, self.player_two,
                            self.player_three]

        except Exception as e:
            logging.error(
                "Game.reset_game(): Unable to reset game\n{}".format(str(e)))

    def update_log_file(self):
        """Updated server.log every .5 seconds"""

        if self.logger_pause_start == 0:
            self.logger_pause_start = time.time()
        else:
            elapsed = time.time() - self.logger_pause_start
            if elapsed > .5:
                logging.info("Game.update_log_file(): {}".format(
                    self.game_state))
                self.logger_pause_start = 0

    def send_game_state(self):
        """Return data for players and wall"""

        # Gather game state data
        self.check_client_player_states()
        self.check_server_game_status()

        # build game state json and return to endpoints
        self.game_state = {
            "game_status": self.game_status,
            "round_durration": self.lap_time_durration,
            "round_over": self.round_over,
            "countdown": self.countdown_remaining,
            "winner_id": self.game_winner_id,
            "winner_time": self.game_winner_time,
            "master_reset": self.master_reset
        }

        # Convert state to json and return
        state = json.dumps(self.game_state)
        self.update_log_file()

        # allow master reset to hold for 3 seconds
        if self.master_reset:
            if self.master_reset_start == 0:
                logging.info("Game.send_game_state(): Starting Master reset")
                self.master_reset_start = time.time()
            else:
                elapsed = time.time() - self.master_reset_start
                if elapsed > 3:
                    logging.info(
                        f"Game.send_game_state(): self.master_reset {self.master_reset}")
                    self.master_reset = False
                    self.master_reset_start = 0

        return state
