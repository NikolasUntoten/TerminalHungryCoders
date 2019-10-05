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

    def evaluate_enemy_defence(self, game_state):
        for i in range(0, 14):
            for j in range(len(self.grid_map[i])):
                board_indices = self.convert_list_index_to_board_index(i, j)
                number_of_attackers = len(game_state.get_attackers(location=board_indices, player_index=1))
                self.grid_map[i][j] = number_of_attackers * 8

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
        self.starter_strategy(game_state)
        self.evaluate_self_defence(game_state)
        self.evaluate_enemy_defence(game_state)
        self.populate_defense(game_state, [13])
        self.__place__attackers__()
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

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # If the turn is less than 5, stall with Scramblers and wait to see enemy's base
        if game_state.turn_number < 5:
            self.stall_with_scramblers(game_state)
        else:
            # Now let's analyze the enemy base to see where their defenses are concentrated.
            # If they have many units in the front we can build a line for our EMPs to attack them at long range.
            if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
                self.emp_line_strategy(game_state)
            else:
                # They don't have many units in the front so lets figure out their least defended area and send Pings there.

                # Only spawn Ping's every other turn
                # Sending more at once is better since attacks can only hit a single ping at a time
                if game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    ping_spawn_location_options = [[13, 0], [14, 0]]
                    best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
                    game_state.attempt_spawn(PING, best_location, 1000)

                # Lastly, if we have spare cores, let's build some Encryptors to boost our Pings' health.
                encryptor_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
                game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place destructors that attack enemy units
        destructor_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations)

        # Place filters in front of destructors to soak up damage for them
        filter_locations = [[8, 12], [19, 12]]
        game_state.attempt_spawn(FILTER, filter_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1] + 1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)

    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own firewalls 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        # While we have remaining bits to spend lets send out scramblers randomly.
        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """

    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        cheapest_unit = FILTER
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost < gamelib.GameUnit(cheapest_unit, game_state.config).cost:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR,
                                                                                             game_state.config).damage
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (
                            valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

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

    def __place_attackers__(self, game_state):
        bits = game_state.get_resource(game_state.BITS)
        if bits < (5 + game_state.turn_number // 10) * 2:
            return None
        start_location, damage = self.__find_best_start_location__(game_state)
        pings, emps, scramblers = self.__find_best_start_unit__(game_state, damage, bits)

        if pings > 0:
            game_state.attempt_spawn(game_state.PING, start_location, pings)
        if emps > 0:
            game_state.attempt_spawn(game_state.EMP, start_location, emps)
        if scramblers > 0:
            game_state.attempt_spawn(game_state.SCRAMBLER, start_location, scramblers)

    def __find_best_start_location__(self, game_state):
        possible_start_locations = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        best_start_location = None
        min_damage = 100000  # damage taken on the path
        min_path_length = 10000
        for start_location in possible_start_locations:
            if game_state.contains_stationary_unit(start_location):
                continue
            path = game_state.find_path_to_edge(start_location)
            damage = sum([8 * len(game_state.get_attackers(location, 0)) for location in path])
            if damage < min_damage or (damage == min_damage and min_path_length < len(path)):
                min_damage = damage
                min_path_length = len(path)
                best_start_location = start_location
        return best_start_location, min_damage

    # returns count of pings, emps, scramblers in order to be placed.
    def __find_best_start_unit__(self, game_state, damage, bits):
        scramblers = 0
        bits = int(bits)

        enemy_bits = game_state.get_resource(game_state.BITS)
        while enemy_bits > 8 and bits > 0:
            scramblers += 1
            enemy_bits -= 8
            bits -= 1

        if damage < 16:
            return bits, 0, scramblers
        count = bits // 4
        return count + bits % 4, count, scramblers


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
