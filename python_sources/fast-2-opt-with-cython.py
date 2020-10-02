#!/usr/bin/env python
# coding: utf-8

# <h2>Using 2-opt with Cython</h2>
# 
# The k-opt algorithm is a local search method that is used in some of the best heuristics for the TSP (e.g. Lin-Kernighan). It's considered a tour improvement heuristic, since we need a initial solution (tour).
# 
# In this notebook I will compare the 2-opt heuristic in Python and Cython. I'm using [this presentation](http://on-demand.gputechconf.com/gtc/2014/presentations/S4534-high-speed-2-opt-tsp-solver.pdf) as reference for the 2-opt algorithm.

# <h3>Prepare inputs</h3>
# 
# To test the speed I'll use only the first 5,000 cities. Coords is a 2d numpy array with coordinates (x, y) and tour is a rank 1 numpy array.

# In[ ]:


import numpy as np
import pandas as pd
cities = pd.read_csv("../input/cities.csv", nrows=5000, index_col=['CityId'])
coords = cities.values
# dummy tour: 0, 1, 2, 3...
tour = np.array([i for i in range(5000)])
print("There are", len(coords), "cities in coords")


# <h3>2 Opt - How does it work?</h3>
# 
# The key idea here is to replace two edges at the same time in a given tour:
# 
# > Find best pair of edges (i, i+1) and
# (j, j+1) such that replacing them with
# (i, j) and (i+1, j+1) minimizes tour length
# 
# We are replacing edges (i, i+1) and (j, j+1) for (i, j) and (i+1, j+1). Since this problem have symmetric distances, the only change in the tour length is between these four cities. The path between i+1 and j will be reversed, but the distance from node A to B is the same from B to A, so the path length wont change.
# 
# We also need the *best pair of edges*, so the algorithm must loop trough all possible combinations of i and j before making the move (update tour). This is a naive approach and more complex heuristics can select a few nodes to try instead of every single combination.
# 
# It's important to calculate distances fast, so I timed a few different functions (math.sqrt, np.linalg, scipy) and the fastest was using np.hypot. The best option would be a pre-computed distance matrix between all cities, but I think we have too many cities for that.

# In[ ]:


def two_opt_python():
    min_change = 0
    num_cities = len(tour)
    # Find the best move
    for i in range(num_cities - 2):
        for j in range(i + 2, num_cities - 1):
            change = dist(i, j) + dist(i+1, j+1) - dist(i, i+1) - dist(j, j+1)
            if change < min_change:
                min_change = change
                min_i, min_j = i, j
    # Update tour with best move
    if min_change < 0:
        tour[min_i+1:min_j+1] = tour[min_i+1:min_j+1][::-1]        

def dist(a, b):
    """Return the euclidean distance between cities tour[a] and tour[b]."""
    return np.hypot(coords[tour[a], 0] - coords[tour[b], 0],
                    coords[tour[a], 1] - coords[tour[b], 1])


# In[ ]:


get_ipython().run_line_magic('time', 'two_opt_python()')


# We should run two_opt_python function until there are no more improvements (min_change >= 0), but as we can see this is extremelly slow even for a single iteration with a small sample...

# <h3>Now with Cython...</h3>
# 
# With Cython we can implement C functions with a python syntax:
# 
# > Cython is an optimising static compiler for both the Python programming language and the extended Cython programming language. The Cython language is a superset of the Python language that additionally supports calling C functions and declaring C types on variables and class attributes. This allows the compiler to generate very efficient C code from Cython code.
# 
# Coords and tour, which are numpy arrays, are passed as [Memoryviews](http://docs.cython.org/en/latest/src/userguide/memoryviews.html) and variables have C static data-types (defined with cdef). Besides that it's pretty much python syntax:

# In[ ]:


get_ipython().run_line_magic('load_ext', 'Cython')


# In[ ]:


get_ipython().run_cell_magic('cython', '', 'import numpy as np\ncimport numpy as np\ncimport cython\nfrom libc.math cimport sqrt\n\ncpdef two_opt_cython(double[:,:] coords, int[:] tour_):\n    cdef float min_change, change\n    cdef int i, j, min_i, min_j, num_cities\n    num_cities = len(tour_)\n    min_change = 0\n    # Find the best move\n    for i in range(num_cities - 2):\n        for j in range(i + 2, num_cities - 1):\n            change = dist(i, j, tour_, coords) + dist(i+1, j+1, tour_, coords)\n            change = - dist(i, i+1, tour_, coords) - dist(j, j+1, tour_, coords)\n            if change < min_change:\n                min_change = change\n                min_i, min_j = i, j\n    # Update tour with best move\n    if min_change < 0:\n        tour_[min_i+1:min_j+1] = tour_[min_i+1:min_j+1][::-1]\n    return np.asarray(tour_)  # memoryview to numpy array\n\ncdef float dist(int a, int b, int[:] tour_view, double[:,:] coords_view):\n    """Return the euclidean distance between cities tour[a] and tour[b]."""\n    return sqrt((coords_view[tour_view[a], 0] - coords_view[tour_view[b], 0])**2 +\n                (coords_view[tour_view[a], 1] - coords_view[tour_view[b], 1])**2)')


# In[ ]:


get_ipython().run_line_magic('time', "two_opt_cython(coords, tour.astype('int32'))")


# Wow! From more than 3 minutes to less than a second. 
# 
# The idea here was to show how usefull Cython can be in this competition - especially for the kernels prize. Using this naive algorithm won't improve the solution found by LKH or Concorde, but it's a good starting point. In the next version I'll try to add the prime penalty to the distance function.