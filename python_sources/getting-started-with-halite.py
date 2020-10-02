#!/usr/bin/env python
# coding: utf-8

# # Getting started

# In[ ]:


get_ipython().run_cell_magic('writefile', 'submission.py', '\n####################\n# Helper functions #\n####################\n\n# Helper function we\'ll use for getting adjacent position with the most halite\ndef argmax(arr, key=None):\n    return arr.index(max(arr, key=key)) if key else arr.index(max(arr))\n\n# Converts position from 1D to 2D representation\ndef get_col_row(size, pos):\n    return (pos % size, pos // size)\n\n# Returns the position in some direction relative to the current position (pos) \ndef get_to_pos(size, pos, direction):\n    col, row = get_col_row(size, pos)\n    if direction == "NORTH":\n        return pos - size if pos >= size else size ** 2 - size + col\n    elif direction == "SOUTH":\n        return col if pos + size >= size ** 2 else pos + size\n    elif direction == "EAST":\n        return pos + 1 if col < size - 1 else row * size\n    elif direction == "WEST":\n        return pos - 1 if col > 0 else (row + 1) * size - 1\n\n# Get positions in all directions relative to the current position (pos)\n# Especially useful for figuring out how much halite is around you\ndef getAdjacent(pos, size):\n    return [\n        get_to_pos(size, pos, "NORTH"),\n        get_to_pos(size, pos, "SOUTH"),\n        get_to_pos(size, pos, "EAST"),\n        get_to_pos(size, pos, "WEST"),\n    ]\n\n# Returns best direction to move from one position (fromPos) to another (toPos)\n# Example: If I\'m at pos 0 and want to get to pos 55, which direction should I choose?\ndef getDirTo(fromPos, toPos, size):\n    fromY, fromX = divmod(fromPos, size)\n    toY,   toX   = divmod(toPos,   size)\n    if fromY < toY: return "SOUTH"\n    if fromY > toY: return "NORTH"\n    if fromX < toX: return "EAST"\n    if fromX > toX: return "WEST"\n\n# Possible directions a ship can move in\nDIRS = ["NORTH", "SOUTH", "EAST", "WEST"]\n# We\'ll use this to keep track of whether a ship is collecting halite or \n# carrying its cargo to a shipyard\nship_states = {}\n\n#############\n# The agent #\n#############\n\ndef agent(obs, config):\n    # Get the player\'s halite, shipyard locations, and ships (along with cargo) \n    player_halite, shipyards, ships = obs.players[obs.player]\n    size = config["size"]\n    # Initialize a dictionary containing commands that will be sent to the game\n    action = {}\n\n    # If there are no ships, use first shipyard to spawn a ship.\n    if len(ships) == 0 and len(shipyards) > 0:\n        uid = list(shipyards.keys())[0]\n        action[uid] = "SPAWN"\n        \n    # If there are no shipyards, convert first ship into shipyard.\n    if len(shipyards) == 0 and len(ships) > 0:\n        uid = list(ships.keys())[0]\n        action[uid] = "CONVERT"\n        \n    for uid, ship in ships.items():\n        if uid not in action: # Ignore ships that will be converted to shipyards\n            pos, cargo = ship # Get the ship\'s position and halite in cargo\n            \n            ### Part 1: Set the ship\'s state \n            if cargo < 200: # If cargo is too low, collect halite\n                ship_states[uid] = "COLLECT"\n            if cargo > 500: # If cargo gets very big, deposit halite\n                ship_states[uid] = "DEPOSIT"\n                \n            ### Part 2: Use the ship\'s state to select an action\n            if ship_states[uid] == "COLLECT":\n                # If halite at current location running low, \n                # move to the adjacent square containing the most halite\n                if obs.halite[pos] < 100:\n                    best = argmax(getAdjacent(pos, size), key=obs.halite.__getitem__)\n                    action[uid] = DIRS[best]\n            \n            if ship_states[uid] == "DEPOSIT":\n                # Move towards shipyard to deposit cargo\n                direction = getDirTo(pos, list(shipyards.values())[0], size)\n                if direction: action[uid] = direction\n                \n    return action')


# In[ ]:


from kaggle_environments import make
env = make("halite", debug=True)
env.run(["submission.py", "random", "random", "random"])
env.render(mode="ipython", width=800, height=600)


# In[ ]:



