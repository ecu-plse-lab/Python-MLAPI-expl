#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# In[ ]:


from kaggle_environments import make, evaluate

# Create the game environment
# Set debug=True to see the errors if your agent refuses to run
env = make("connectx", debug=True)


# In[ ]:


def my_agent(obs, config):
    import numpy as np # linear algebra
    import random
    N_STEPS = 3
    
    def drop_piece(grid, col, piece, config):
        next_grid = grid.copy()
        for row in range(config.rows-1, -1, -1):
            if next_grid[row][col] == 0:
                break
        next_grid[row][col] = piece
        return next_grid

    # Returns True if dropping piece in column results in game win
    def check_winning_move(obs, config, col, piece):
        # Convert the board to a 2D grid
        grid = np.asarray(obs.board).reshape(config.rows, config.columns)
        next_grid = drop_piece(grid, col, piece, config)
        # horizontal
        for row in range(config.rows):
            for col in range(config.columns-(config.inarow-1)):
                window = list(next_grid[row,col:col+config.inarow])
                if window.count(piece) == config.inarow:
                    return True
        # vertical
        for row in range(config.rows-(config.inarow-1)):
            for col in range(config.columns):
                window = list(next_grid[row:row+config.inarow,col])
                if window.count(piece) == config.inarow:
                    return True
        # positive diagonal
        for row in range(config.rows-(config.inarow-1)):
            for col in range(config.columns-(config.inarow-1)):
                window = list(next_grid[range(row, row+config.inarow), range(col, col+config.inarow)])
                if window.count(piece) == config.inarow:
                    return True
        # negative diagonal
        for row in range(config.inarow-1, config.rows):
            for col in range(config.columns-(config.inarow-1)):
                window = list(next_grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
                if window.count(piece) == config.inarow:
                    return True
        return False
    
    def score_move(grid, col, mark, config, nsteps):
        next_grid = drop_piece(grid, col, mark, config)
        score = minimax(next_grid, nsteps-1, False, mark, config)
        return score
    
    def get_heuristic(grid, mark, config):
        num_twos = count_windows(grid, 2, mark, config)
        num_threes = count_windows(grid, 3, mark, config)
        num_fours = count_windows(grid, 4, mark, config)
        num_twos_opp = count_windows(grid, 2, mark%2+1, config)
        num_threes_opp = count_windows(grid, 3, mark%2+1, config)
        num_fours_opp =count_windows(grid, 4, mark%2+1, config)
        score = 100000*num_fours + 50**num_threes + 5*num_twos + -2*num_twos_opp + -(10**num_threes_opp) + -10000*num_fours_opp
        return score
    
    def check_window(window, num_discs, piece, config):
        return (window.count(piece) == num_discs and window.count(0) == config.inarow-num_discs)
    
    # Helper function for get_heuristic: counts number of windows satisfying specified heuristic conditions
    def count_windows(grid, num_discs, piece, config):
        num_windows = 0
        for row in range(config.rows):
            for col in range(config.columns):
                if col < config.columns-(config.inarow-1):
                    window = list(grid[row, col:col+config.inarow])
                    if check_window(window, num_discs, piece, config):
                        num_windows += 1
                if row < config.rows-(config.inarow-1):
                    window = list(grid[row:row+config.inarow, col])
                    if check_window(window, num_discs, piece, config):
                        num_windows += 1
                if row < config.rows-(config.inarow-1) and col < config.columns-(config.inarow-1):
                    window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
                    if check_window(window, num_discs, piece, config):
                        num_windows += 1
                if row > config.inarow-1 and col < config.columns-(config.inarow-1):
                    window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
                    if check_window(window, num_discs, piece, config):
                        num_windows += 1
        return num_windows
    
    def minimax(node, depth, maximizingPlayer, mark, config):
        is_terminal = is_terminal_node(node, config)
        valid_moves = [c for c in range(config.columns) if node[0][c] == 0]
        if depth == 0 or is_terminal:
            return get_heuristic(node, mark, config)
        if maximizingPlayer:
            value = -np.Inf
            for col in valid_moves:
                child = drop_piece(node, col, mark, config)
                value = max(value, minimax(child, depth-1, False, mark, config))
            return value
        else:
            value = np.Inf
            for col in valid_moves:
                child = drop_piece(node, col, mark%2+1, config)
                value = min(value, minimax(child, depth-1, True, mark, config))
            return value
    
    def is_terminal_node(grid, config):
        # Check for draw 
        if list(grid[0, :]).count(0) == 0:
            return True
        #Check win for either player
        if count_windows(grid, 4, 1, config) >= 1 or count_windows(grid, 4, 2, config) >= 1:
            return True
        return False 
    
    valid_moves = [c for c in range(config.columns) if obs.board[c] == 0]
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    scores = dict(zip(valid_moves, [score_move(grid, col, obs.mark, config, N_STEPS) for col in valid_moves]))
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
    if 3 in max_cols:
        return 3
    else: 
        return random.choice(max_cols)


# In[ ]:


env = make("connectx")

env.run(["random", my_agent])

env.render(mode="ipython")


# In[ ]:


def get_win_percentages(agent1, agent2, n_rounds=50):
    # Use default Connect Four setup
    config = {'rows': 6, 'columns': 7, 'inarow': 4}
    # Agent 1 goes first (roughly) half the time          
    outcomes = evaluate("connectx", [agent1, agent2], config, [], n_rounds//2)
    # Agent 2 goes first (roughly) half the time      
    outcomes += [[b,a] for [a,b] in evaluate("connectx", [agent2, agent1], config, [], n_rounds-n_rounds//2)]
    print("Agent 1 Win Percentage:", np.round(outcomes.count([1,0])/len(outcomes), 2))
    print("Agent 2 Win Percentage:", np.round(outcomes.count([0,1])/len(outcomes), 2))
    print("Number of Invalid Plays by Agent 1:", outcomes.count([None, 0.5]))
    print("Number of Invalid Plays by Agent 2:", outcomes.count([0.5, None]))
    print("Number of Draws (in {} game rounds):".format(n_rounds), outcomes.count([0.5, 0.5]))


#get_win_percentages(agent1=my_agent, agent2="random")


# In[ ]:


import inspect
import os

def write_agent_to_file(function, file):
    with open(file, "a" if os.path.exists(file) else "w") as f:
        f.write(inspect.getsource(function))
        print(function, "written to", file)

write_agent_to_file(my_agent, "submission.py")


# In[ ]:


import sys
from kaggle_environments import utils

out = sys.stdout
submission = utils.read_file("/kaggle/working/submission.py")
agent = utils.get_last_callable(submission)
sys.stdout = out

env = make("connectx", debug=True)
env.run([my_agent, my_agent])
print("Success!" if env.state[0].status == env.state[1].status == "DONE" else "Failed...")
