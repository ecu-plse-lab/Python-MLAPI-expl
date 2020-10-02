#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python

# For example, here's several helpful packages to load in 
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Performance metrics
from sklearn.metrics import pairwise_distances
from scipy.stats import spearmanr


# In[ ]:


# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory
import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.


# In[ ]:


# Read data
simplex999 = pd.read_csv('../input/nicn/simlex999_rus_without_dupl.csv')
simplex999.head()


# In[ ]:


# Plot the distribution of original distances
sns.distplot(simplex999.distance_i_j, kde_kws={'shade':True,'color':'red','bw':0.1});


# In[ ]:


# Split words in pairs
simplex999['word_i'] = [pair[0] for pair in simplex999.word_i_word_j.str.split('_')]
simplex999['word_j'] = [pair[1] for pair in simplex999.word_i_word_j.str.split('_')]
simplex999.head()


# In[ ]:


# Collect unique words
vocabulary = sorted({x for pair in [s.split('_') for s in simplex999.word_i_word_j] for x in pair})
wordnum = len(vocabulary)
print(wordnum)


# In[ ]:


# Enumerate the words
indexVoc = dict(zip(vocabulary,range(wordnum)))


# In[ ]:


# Index the words
simplex999['wid_i'] = [indexVoc[w] for w in simplex999.word_i]
simplex999['wid_j'] = [indexVoc[w] for w in simplex999.word_j]
simplex999.head()


# In[ ]:


# Create symmetric distance matrix
origdistmatrix = np.empty((wordnum,wordnum))
origdistmatrix[:,:] = np.NaN
origdistmatrix[simplex999.wid_i,simplex999.wid_j] = simplex999.distance_i_j
origdistmatrix[simplex999.wid_j,simplex999.wid_i] = simplex999.distance_i_j


# In[ ]:


# Metric spaces do not support non-trivial reflexion
origdistmatrix[np.arange(wordnum),np.arange(wordnum)] =  10
# Metric spaces do not support non-symmetric distances
origdistmatrix = (origdistmatrix + origdistmatrix.T)/2


# In[ ]:


# Plot relation
sns.scatterplot(simplex999.distance_i_j, origdistmatrix[simplex999.wid_i,simplex999.wid_j]);
spearmanr(simplex999.distance_i_j, origdistmatrix[simplex999.wid_i,simplex999.wid_j])


# In[ ]:





# In[ ]:


# Transform assessor scores to metric distances
origdistmatrix_for_nMDS = np.nan_to_num( 2-origdistmatrix/10, nan=0.0)
origdistmatrix_for_nMDS[np.arange(wordnum),np.arange(wordnum)] =  0


# In[ ]:


# Plot relation
sns.scatterplot(simplex999.distance_i_j, origdistmatrix_for_nMDS[simplex999.wid_i,simplex999.wid_j]);
spearmanr(simplex999.distance_i_j, origdistmatrix_for_nMDS[simplex999.wid_i,simplex999.wid_j])


# In[ ]:


from sklearn.manifold import MDS
nMDS=MDS(n_components=5, dissimilarity='precomputed', metric=False, n_init=30, max_iter=500)
X=nMDS.fit_transform(origdistmatrix_for_nMDS)


# In[ ]:


sns.scatterplot(X[:,0],X[:,1]);


# In[ ]:


deriveddistmatrix=pairwise_distances(X)


# In[ ]:


# Plot relation
sns.scatterplot(simplex999.distance_i_j, deriveddistmatrix[simplex999.wid_i,simplex999.wid_j]);
spearmanr(simplex999.distance_i_j, deriveddistmatrix[simplex999.wid_i,simplex999.wid_j])


# In[ ]:



