#!/usr/bin/env python
# coding: utf-8

# # Install kaggle-environments

# In[ ]:


# 1. Enable Internet in the Kernel (Settings side pane)

# 2. Curl cache may need purged if v0.1.6 cannot be found (uncomment if needed). 
# !curl -X PURGE https://pypi.org/simple/kaggle-environments

# Halite environment was defined in v0.2.1
get_ipython().system("pip install 'kaggle-environments>=0.2.1'")


# # Create Halite Environment

# In[ ]:


from kaggle_environments import evaluate, make

env = make("halite", debug=True)
env.render()


# # Create a Submission (agent)

# In[ ]:


get_ipython().run_cell_magic('writefile', 'submission.py', '# for Debug previous line (%%writefile submission.py) should be commented out, uncomment to write submission.py\n\n#FUNCTIONS###################################################\ndef get_map_and_average_halite(obs):\n    """\n        get average amount of halite per halite source\n        and map as two dimensional array of objects and set amounts of halite in each cell\n    """\n    game_map = []\n    halite_sources_amount = 0\n    halite_total_amount = 0\n    for x in range(conf.size):\n        game_map.append([])\n        for y in range(conf.size):\n            game_map[x].append({\n                # value will be ID of owner\n                "shipyard": None,\n                # value will be ID of owner\n                "ship": None,\n                # value will be amount of halite\n                "ship_cargo": None,\n                # amount of halite\n                "halite": obs.halite[conf.size * y + x]\n            })\n            if game_map[x][y]["halite"] > 0:\n                halite_total_amount += game_map[x][y]["halite"]\n                halite_sources_amount += 1\n    average_halite = halite_total_amount / halite_sources_amount\n    return game_map, average_halite\n\ndef get_swarm_units_coords_and_update_map(s_env):\n    """ get lists of coords of Swarm\'s units and update locations of ships and shipyards on the map """\n    # arrays of (x, y) coords\n    swarm_shipyards_coords = []\n    swarm_ships_coords = []\n    # place on the map locations of units of every player\n    for player in range(len(s_env["obs"].players)):\n        # place on the map locations of every shipyard of the player\n        shipyards = list(s_env["obs"].players[player][1].values())\n        for shipyard in shipyards:\n            x = shipyard % conf.size\n            y = shipyard // conf.size\n            # place shipyard on the map\n            s_env["map"][x][y]["shipyard"] = player\n            if player == s_env["obs"].player:\n                swarm_shipyards_coords.append((x, y))\n        # place on the map locations of every ship of the player\n        ships = list(s_env["obs"].players[player][2].values())\n        for ship in ships:\n            x = ship[0] % conf.size\n            y = ship[0] // conf.size\n            # place ship on the map\n            s_env["map"][x][y]["ship"] = player\n            s_env["map"][x][y]["ship_cargo"] = ship[1]\n            if player == s_env["obs"].player:\n                swarm_ships_coords.append((x, y))\n    return swarm_shipyards_coords, swarm_ships_coords\n\ndef get_c(c):\n    """ get coordinate, considering donut type of the map """\n    return c % conf.size\n\ndef clear(x, y, player, game_map):\n    """ check if cell is safe to move in """\n    # if there is no shipyard, or there is player\'s shipyard\n    # and there is no ship\n    if ((game_map[x][y]["shipyard"] == player or game_map[x][y]["shipyard"] == None) and\n            game_map[x][y]["ship"] == None):\n        return True\n    return False\n\ndef return_to_shipyard(x_initial, y_initial, actions, s_env, ship_index):\n    """ return to shipyard\'s coords """\n    ship_id = s_env["ships_keys"][ship_index]\n    ship_cargo = s_env["ships_values"][ship_index][1]\n    # if ship is currently at shipyard\'s coords\n    if x_initial == shipyard_coords["x"] and y_initial == shipyard_coords["y"]:\n        # if there is no shipyard at shipyard\'s coords\n        if (s_env["map"][x_initial][y_initial]["shipyard"] == None and\n                (ship_cargo + s_env["swarm_halite"]) >= conf.convertCost):\n            actions[ship_id] = "CONVERT"\n            s_env["map"][x_initial][y_initial]["ship"] = None\n            return True\n        # if ship is going to move out from shipyard\'s coords\n        else:\n            global movement_tactics_index\n            ships_data[ship_id]["moves_done"] = 0\n            ships_data[ship_id]["ship_max_moves"] = 1\n            ships_data[ship_id]["trail"] = []\n            ships_data[ship_id]["directions"] = movement_tactics[movement_tactics_index]["directions"]\n            ships_data[ship_id]["directions_index"] = 0\n            movement_tactics_index += 1\n            if movement_tactics_index >= movement_tactics_amount:\n                movement_tactics_index = 0\n    else:\n        # if ship has to return to shipyard\'s coords\n        if ship_cargo >= return_threshold:\n            x = trail_directions[ships_data[ship_id]["trail"][-1]]["x"](x_initial)\n            y = trail_directions[ships_data[ship_id]["trail"][-1]]["y"](y_initial)\n            # if cell is safe to move in\n            if (clear(x, y, s_env["obs"].player, s_env["map"]) and\n                    not hostile_ship_near(x, y, s_env["obs"].player, s_env["map"], ship_cargo)):\n                s_env["map"][x_initial][y_initial]["ship"] = None\n                s_env["map"][x][y]["ship"] = s_env["obs"].player\n                actions[ship_id] = trail_directions[ships_data[ship_id]["trail"][-1]]["direction"]\n                ships_data[ship_id]["trail"].pop()\n                return True\n    return False\n\ndef move_ship(x_initial, y_initial, actions, s_env, ship_index):\n    """ move the ship according to first acceptable tactic """\n    ok = go_for_halite(x_initial, y_initial, s_env["ships_keys"][ship_index], actions, s_env, ship_index)\n    if ok:\n        return\n    standard_patrol(x_initial, y_initial, s_env["ships_keys"][ship_index], actions, s_env, ship_index)\n\ndef go_for_halite(x_initial, y_initial, ship_id, actions, s_env, ship_index):\n    """ ship will go to safe cell with enough halite, if it is found """\n    # if current cell has enough halite\n    if (s_env["map"][x_initial][y_initial]["halite"] > s_env["low_amount_of_halite"] and\n            not hostile_ship_near(x_initial, y_initial, s_env["obs"].player, s_env["map"], s_env["ships_values"][ship_index][1])):\n        most_halite = s_env["map"][x_initial][y_initial]["halite"]\n    else:\n        # biggest amount of halite among scanned cells\n        most_halite = s_env["low_amount_of_halite"]\n    direction = None\n    for d in range(len(directions_list)):\n        x = directions_list[d]["x"](x_initial)\n        y = directions_list[d]["y"](y_initial)\n        # if cell is safe to move in\n        if (clear(x, y, s_env["obs"].player, s_env["map"]) and\n                not hostile_ship_near(x, y, s_env["obs"].player, s_env["map"], s_env["ships_values"][ship_index][1])):\n            # if current cell has more than biggest amount of halite\n            if s_env["map"][x][y]["halite"] > most_halite:\n                most_halite = s_env["map"][x][y]["halite"]\n                direction = directions_list[d]["direction"]\n                direction_x = x\n                direction_y = y\n    # if cell is safe to move in and has substantial amount of halite\n    if most_halite > s_env["low_amount_of_halite"] and direction != None:\n        actions[ship_id] = direction\n        ships_data[ship_id]["trail"].append(direction)\n        s_env["map"][x_initial][y_initial]["ship"] = None\n        s_env["map"][direction_x][direction_y]["ship"] = s_env["obs"].player\n        return True\n    # if current cell has biggest amount of halite\n    elif most_halite == s_env["map"][x_initial][y_initial]["halite"]:\n        return True\n    return False\n\ndef standard_patrol(x_initial, y_initial, ship_id, actions, s_env, ship_index):\n    """ \n        ship will move in expanding circles clockwise or counterclockwise\n        until reaching maximum radius, then radius will be minimal again\n    """\n    directions = ships_data[ship_id]["directions"]\n    # set index of direction\n    i = ships_data[ship_id]["directions_index"]\n    for j in range(len(directions)):\n        x = directions[i]["x"](x_initial)\n        y = directions[i]["y"](y_initial)\n        # if cell is ok to move in\n        if (clear(x, y, s_env["obs"].player, s_env["map"]) and\n                (s_env["map"][x][y]["shipyard"] == s_env["obs"].player or\n                not hostile_ship_near(x, y, s_env["obs"].player, s_env["map"], s_env["ships_values"][ship_index][1]))):\n            ships_data[ship_id]["moves_done"] += 1\n            # apply changes to game_map, to avoid collisions of player\'s ships next turn\n            s_env["map"][x_initial][y_initial]["ship"] = None\n            s_env["map"][x][y]["ship"] = s_env["obs"].player\n            # if it was last move in this direction\n            if ships_data[ship_id]["moves_done"] >= ships_data[ship_id]["ship_max_moves"]:\n                ships_data[ship_id]["moves_done"] = 0\n                ships_data[ship_id]["directions_index"] += 1\n                # if it is last direction in a list\n                if ships_data[ship_id]["directions_index"] >= len(directions):\n                    ships_data[ship_id]["directions_index"] = 0\n                    ships_data[ship_id]["ship_max_moves"] += 1\n                    # if ship_max_moves reached maximum radius expansion\n                    if ships_data[ship_id]["ship_max_moves"] > max_moves_amount:\n                        ships_data[ship_id]["ship_max_moves"] = 2\n            actions[ship_id] = directions[i]["direction"]\n            ships_data[ship_id]["trail"].append(directions[i]["direction"])\n            break\n        else:\n            # loop through directions\n            i += 1\n            if i >= len(directions):\n                i = 0\n\ndef get_directions(i0, i1, i2, i3):\n    """ get list of directions in a certain sequence """\n    return [directions_list[i0], directions_list[i1], directions_list[i2], directions_list[i3]]\n\ndef hostile_ship_near(x, y, player, m, cargo):\n    """ check if hostile ship is in one move away from game_map[x][y] and has less or equal halite """\n    # m = game map\n    n = get_c(y - 1)\n    e = get_c(x + 1)\n    s = get_c(y + 1)\n    w = get_c(x - 1)\n    if (\n            (m[x][n]["ship"] != player and m[x][n]["ship"] != None and m[x][n]["ship_cargo"] <= cargo) or\n            (m[x][s]["ship"] != player and m[x][s]["ship"] != None and m[x][s]["ship_cargo"] <= cargo) or\n            (m[e][y]["ship"] != player and m[e][y]["ship"] != None and m[e][y]["ship_cargo"] <= cargo) or\n            (m[w][y]["ship"] != player and m[w][y]["ship"] != None and m[w][y]["ship_cargo"] <= cargo)\n        ):\n        return True\n    return False\n\ndef spawn_ship(actions, s_env, ships_amount, i):\n    """ spawn ship, if possible """\n    if s_env["swarm_halite"] >= min_halite_to_spawn and ships_amount < s_env["ships_max_amount"]:\n        x = s_env["swarm_shipyards_coords"][i][0]\n        y = s_env["swarm_shipyards_coords"][i][1]\n        # if there is currently no ship at shipyard\n        if clear(x, y, s_env["obs"].player, s_env["map"]):\n            s_env["swarm_halite"] -= conf.spawnCost\n            actions[s_env["shipyards_keys"][i]] = "SPAWN"\n            s_env["map"][x][y]["ship"] = s_env["obs"].player\n            ships_amount += 1\n        return True, ships_amount\n    return False, ships_amount\n\ndef this_is_new_ship(s_env, i):\n    """ add this ship to ships_data """\n    global movement_tactics_index\n    ships_data[s_env["ships_keys"][i]] = {\n        "moves_done": 0,\n        "ship_max_moves": 1,\n        "trail": [],\n        "directions": movement_tactics[movement_tactics_index]["directions"],\n        "directions_index": 0\n    }\n    movement_tactics_index += 1\n    if movement_tactics_index >= movement_tactics_amount:\n        movement_tactics_index = 0\n\ndef this_is_last_step(x, y, actions, s_env, i):\n    """ actions of ship, if it is last step """\n    if s_env["obs"].step == (conf.episodeSteps - 2) and s_env["ships_values"][i][1] >= conf.convertCost:\n        actions[s_env["ships_keys"][i]] = "CONVERT"\n        s_env["map"][x][y]["ship"] = None\n        return True\n    return False\n\ndef to_spawn_or_not_to_spawn(s_env):\n    """ to spawn, or not to spawn, that is the question """\n    # get ships_max_amount to decide whether to spawn new ships or not\n    ships_max_amount = (conf.episodeSteps - s_env["obs"].step) // 20\n    # if ships_max_amount is less than minimal allowed amount of ships in the Swarm\n    if ships_max_amount < ships_min_amount:\n        ships_max_amount = ships_min_amount\n    return ships_max_amount\n\ndef define_some_globals(observation, configuration):\n    """ define some of the global variables """\n    global conf\n    global return_threshold\n    global max_moves_amount\n    global min_halite_to_spawn\n    global globals_not_defined\n    conf = configuration\n    return_threshold = 1\n    max_moves_amount = 7\n    # set coords of the shipyard\n    start_ship_coords = list(observation.players[observation.player][2].values())[0][0]\n    shipyard_coords["x"] = start_ship_coords % conf.size\n    shipyard_coords["y"] = start_ship_coords // conf.size\n    min_halite_to_spawn = conf.spawnCost + conf.convertCost - return_threshold\n    globals_not_defined = False\n\ndef adapt_environment(observation, configuration, s_env):\n    """ adapt environment for the Swarm """\n    s_env["obs"] = observation\n    if globals_not_defined:\n        define_some_globals(observation, configuration)\n    s_env["map"], s_env["average_halite"] = get_map_and_average_halite(s_env["obs"])\n    s_env["low_amount_of_halite"] = 4 if s_env["average_halite"] < 4 else s_env["average_halite"]\n    s_env["swarm_halite"] = s_env["obs"].players[s_env["obs"].player][0]\n    s_env["swarm_shipyards_coords"], s_env["swarm_ships_coords"] = get_swarm_units_coords_and_update_map(s_env)\n    s_env["ships_keys"] = list(s_env["obs"].players[s_env["obs"].player][2].keys())\n    s_env["ships_values"] = list(s_env["obs"].players[s_env["obs"].player][2].values())\n    s_env["shipyards_keys"] = list(s_env["obs"].players[s_env["obs"].player][1].keys())\n    s_env["ships_max_amount"] = to_spawn_or_not_to_spawn(s_env)\n    \ndef actions_of_ships(actions, s_env):\n    """ actions of every ship of the Swarm """\n    for i in range(len(s_env["swarm_ships_coords"])):\n        x = s_env["swarm_ships_coords"][i][0]\n        y = s_env["swarm_ships_coords"][i][1]\n        # if this is a new ship\n        if s_env["ships_keys"][i] not in ships_data:\n            this_is_new_ship(s_env, i)\n        # if it is last step\n        ok = this_is_last_step(x, y, actions, s_env, i)\n        if ok:\n            continue\n        # if ship has to return to shipyard\n        ok = return_to_shipyard(x, y, actions, s_env, i)\n        if ok:\n            continue\n        move_ship(x, y, actions, s_env, i)\n\ndef actions_of_shipyards(actions, s_env):\n    """ actions of every shipyard of the Swarm """\n    ships_amount = len(s_env["ships_keys"])\n    # spawn ships from every shipyard, if possible\n    for i in range(len(s_env["shipyards_keys"])):\n        ok, ships_amount = spawn_ship(actions, s_env, ships_amount, i)\n        if not ok:\n            break\n\n\n#GLOBAL_VARIABLES#############################################\nconf = None\n# max amount of moves in one direction before turning\nmax_moves_amount = None\n# threshold of harvested by a ship halite to return to shipyard\nreturn_threshold = None\n# object with ship ids and their data\nships_data = {}\n# initial movement_tactics index\nmovement_tactics_index = 0\n# minimum amount of ships that should be in the Swarm at any time\nships_min_amount = 3\n# coords of the shipyard\nshipyard_coords = {"x": None, "y": None}\n# minimal amount of halite to spawn a ship\nmin_halite_to_spawn = None\n# not all global variables are defined\nglobals_not_defined = True\n\n# list of directions\ndirections_list = [\n    {\n        "direction": "NORTH",\n        "x": lambda z: z,\n        "y": lambda z: get_c(z - 1)\n    },\n    {\n        "direction": "EAST",\n        "x": lambda z: get_c(z + 1),\n        "y": lambda z: z\n    },\n    {\n        "direction": "SOUTH",\n        "x": lambda z: z,\n        "y": lambda z: get_c(z + 1)\n    },\n    {\n        "direction": "WEST",\n        "x": lambda z: get_c(z - 1),\n        "y": lambda z: z\n    }\n]\n\n# dictionary of trail directions\ntrail_directions = {\n    "NORTH": {\n        "direction": "SOUTH",\n        "x": lambda z: z,\n        "y": lambda z: get_c(z + 1)\n    },\n    "SOUTH": {\n        "direction": "NORTH",\n        "x": lambda z: z,\n        "y": lambda z: get_c(z - 1)\n    },\n    "EAST": {\n        "direction": "WEST",\n        "x": lambda z: get_c(z - 1),\n        "y": lambda z: z\n    },\n    "WEST": {\n        "direction": "EAST",\n        "x": lambda z: get_c(z + 1),\n        "y": lambda z: z\n    }\n}\n\n# list of movement tactics\nmovement_tactics = [\n    # N -> E -> S -> W\n    {"directions": get_directions(0, 1, 2, 3)},\n    # S -> E -> N -> W\n    {"directions": get_directions(2, 1, 0, 3)},\n    # N -> W -> S -> E\n    {"directions": get_directions(0, 3, 2, 1)},\n    # S -> W -> N -> E\n    {"directions": get_directions(2, 3, 0, 1)},\n    # E -> N -> W -> S\n    {"directions": get_directions(1, 0, 3, 2)},\n    # W -> S -> E -> N\n    {"directions": get_directions(3, 2, 1, 0)},\n    # E -> S -> W -> N\n    {"directions": get_directions(1, 2, 3, 0)},\n    # W -> N -> E -> S\n    {"directions": get_directions(3, 0, 1, 2)}\n]\nmovement_tactics_amount = len(movement_tactics)\n\n\n#THE_SWARM####################################################\ndef swarm_agent(observation, configuration):\n    """ RELEASE THE SWARM!!! """\n    s_env = {}\n    actions = {}\n    adapt_environment(observation, configuration, s_env)\n    actions_of_ships(actions, s_env)\n    actions_of_shipyards(actions, s_env)\n    return actions')


# # Debug your Agent

# In[ ]:


if "swarm_agent" in globals():
    # reset variables
    ships_data = {}
    movement_tactics_index = 0

    # Play as first position against random agent.
    trainer = env.train([None, "random"])

    observation = trainer.reset()

    while not env.done:
        my_action = swarm_agent(observation, env.configuration)
        print("Step: {0}, My Action: {1}".format(observation.step, my_action))
        observation, reward, done, info = trainer.step(my_action)
        # env.render(mode="ipython", width=100, height=90, header=False, controls=False)
    env.render()


# # Evaluate your Agent

# In[ ]:


def mean_reward(rewards):
    wins = 0
    ties = 0
    loses = 0
    for r in rewards:
        r0 = 0 if r[0] is None else r[0]
        r1 = 0 if r[1] is None else r[1]
        if r0 > r1:
            wins += 1
        elif r1 > r0:
            loses += 1
        else:
            ties += 1
    return f'wins={wins/len(rewards)}, ties={ties/len(rewards)}, loses={loses/len(rewards)}'

# Run multiple episodes to estimate its performance.
# Setup agentExec as LOCAL to run in memory (runs faster) without process isolation.
print("Swarm Agent vs Random Agent:", mean_reward(evaluate(
    "halite",
    ["submission.py", "random", "random", "random"],
    num_episodes=10, configuration={"agentExec": "LOCAL"}
)))


# # Test your Agent

# In[ ]:


env.run(["submission.py", "submission.py", "submission.py", "submission.py"])
#env.run(["submission.py", "random", "random", "random"])
env.render(mode="ipython", width=800, height=600)


# # Submit to Competition
# 
# 1. Commit this kernel.
# 2. View the commited version.
# 3. Go to "Data" section and find submission.py file.
# 4. Click "Submit to Competition"
# 5. Go to [My Submissions](https://kaggle.com/c/halite/submissions) to view your score and episodes being played.