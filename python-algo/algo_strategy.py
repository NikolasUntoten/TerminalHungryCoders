import gamelib
import random
import math
import warnings
from sys import maxsize
import json
import time

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))
        self.grid_map = []
        j_start = 13
        j_end = 15
        for i in range(0, 14):
            self.grid_map.append([0] * (j_end - j_start))
            j_start -= 1
            j_end += 1
        j_start = 0
        j_end = 28
        for i in range(14, 28):
            self.grid_map.append([0] * (j_end - j_start))
            j_start += 1
            j_end -= 1

    def convert_list_index_to_board_index(self, y, x):
        row = 27 - y
        if y in range(0, 14):
            col = 13 + x - y
        else:
            col = 13 + x - row
        return [col, row]

    def convert_board_index_to_list(self, col, row):
        y = 27 - row
        if y in range(0, 14):
            x = -13 + col + y
        else:
            x = -13 + col + row
        return [y, x]

    def evaluate_self_defence(self, game_state):
        for i in range(14, len(self.grid_map)):
            for j in range(len(self.grid_map[i])):
                board_indices = self.convert_list_index_to_board_index(i, j)
                number_of_attackers = len(game_state.get_attackers(location=board_indices, player_index=0))
                self.grid_map[i][j] = number_of_attackers * 8
        print(self.grid_map)

    def evaluate_enemy_defence(self, game_state):
        for i in range(0, 14):
            for j in range(len(self.grid_map[i])):
                board_indices = self.convert_list_index_to_board_index(i, j)
                number_of_attackers = len(game_state.get_attackers(location=board_indices, player_index=1))
                self.grid_map[i][j] = number_of_attackers * 8
        print(self.grid_map)

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # This is a good place to do initial setup
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  # Comment or remove this line to enable warnings.
        self.evaluate_self_defence(game_state)
        self.evaluate_enemy_defence(game_state)
        self.populate_defense(game_state, [13])
        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def populate_defense(self, game_state, defense_holes_x):
        defense_locations = []
        defense_priority = [DESTRUCTOR, FILTER, ENCRYPTOR]
        temp = [
            [0, 0, 0, 6, 16, 6, 0, 0, 0],
            [1, 0, 2, 6, 10, 6, 2, 0, 1],
            [4, 0, 2, 6, 4, 6, 2, 0, 4],
            [5, 1, 3, 5, 0, 5, 3, 1, 5],
            [6, 1, 4, 3, 0, 3, 4, 1, 6],
            [7, 2, 5, 0, 0, 0, 5, 2, 7],
            [8, 2, 4, 0, 0, 0, 4, 2, 8],
            [9, 2, 3, 0, 0, 0, 3, 2, 9],
            [10, 2, 2, 0, 0, 0, 2, 2, 10],
            [11, 1, 2, 0, 0, 0, 2, 1, 11],
            [12, 1, 1, 0, 0, 0, 1, 1, 12],
            [13, 1, 0, 0, 0, 0, 0, 1, 13],
            [0, 0, 0, 0, 28, 0, 0, 0, 0],
            [0, 0, 0, 0, 28, 0, 0, 0, 0]]
        for row in temp:
            defense_locations.append(
                ([None] * row[0]) +
                ([ENCRYPTOR] * row[1]) +
                ([DESTRUCTOR] * row[2]) +
                ([FILTER] * row[3]) +
                ([None] * row[4]) +
                ([FILTER] * row[5]) +
                ([DESTRUCTOR] * row[6]) +
                ([ENCRYPTOR] * row[7]) +
                ([None] * row[8]))

        threshold = 16.0
        start_time = time.time()
        for defense_type in defense_priority:
            if time.time() - start_time > 1.9:
                break
            running = True
            while game_state.get_resource(game_state.CORES) >= 1.0 and running:
                if time.time() - start_time > 1.9:
                    break
                # find the min defense square
                min_loc = [0, 0]
                for x in range(14, len(self.grid_map)):
                    if time.time() - start_time > 1.9:
                        break
                    for y in range(len(self.grid_map[x])):
                        if time.time() - start_time > 1.9:
                            break
                        if self.grid_map[x][y] < self.grid_map[min_loc[0]][min_loc[1]] \
                                and defense_locations[x][y] is defense_type:
                            min_loc = [x, y]
                # buff said square (if it needs it)
                if self.grid_map[min_loc[0]][min_loc[1]] < threshold \
                        and min_loc[0] not in defense_holes_x:
                    if time.time() - start_time > 1.9:
                        break
                    spawns = game_state.attempt_spawn(unit_type=defense_type,
                                                      locations=self.convert_list_index_to_board_index(min_loc[0],
                                                                                                       min_loc[1]),
                                                      num=1)
                    if spawns > 0:
                        if time.time() - start_time > 1.9:
                            break
                        self.evaluate_self_defence(game_state)
                else:
                    running = False

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
