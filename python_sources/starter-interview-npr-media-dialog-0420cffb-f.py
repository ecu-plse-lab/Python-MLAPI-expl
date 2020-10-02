#!/usr/bin/env python
# coding: utf-8

# ## Introduction
# Greetings from the Kaggle bot! This is an automatically-generated kernel with starter code demonstrating how to read in the data and begin exploring. Click the blue "Edit Notebook" or "Fork Notebook" button at the top of this kernel to begin editing.

# ## Exploratory Analysis
# To begin this exploratory analysis, first use `matplotlib` to import libraries and define functions for plotting the data. Depending on the data, not all plots will be made. (Hey, I'm just a kerneling bot, not a Kaggle Competitions Grandmaster!)

# In[ ]:


from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt # plotting
import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)


# There are 3 csv files in the current version of the dataset:
# 

# In[ ]:


for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))


# The next hidden code cells define functions for plotting data. Click on the "Code" button in the published kernel to reveal the hidden code.

# In[ ]:


# Distribution graphs (histogram/bar graph) of column data
def plotPerColumnDistribution(df, nGraphShown, nGraphPerRow):
    nunique = df.nunique()
    df = df[[col for col in df if nunique[col] > 1 and nunique[col] < 50]] # For displaying purposes, pick columns that have between 1 and 50 unique values
    nRow, nCol = df.shape
    columnNames = list(df)
    nGraphRow = (nCol + nGraphPerRow - 1) / nGraphPerRow
    plt.figure(num = None, figsize = (6 * nGraphPerRow, 8 * nGraphRow), dpi = 80, facecolor = 'w', edgecolor = 'k')
    for i in range(min(nCol, nGraphShown)):
        plt.subplot(nGraphRow, nGraphPerRow, i + 1)
        columnDf = df.iloc[:, i]
        if (not np.issubdtype(type(columnDf.iloc[0]), np.number)):
            valueCounts = columnDf.value_counts()
            valueCounts.plot.bar()
        else:
            columnDf.hist()
        plt.ylabel('counts')
        plt.xticks(rotation = 90)
        plt.title(f'{columnNames[i]} (column {i})')
    plt.tight_layout(pad = 1.0, w_pad = 1.0, h_pad = 1.0)
    plt.show()


# In[ ]:


# Correlation matrix
def plotCorrelationMatrix(df, graphWidth):
    filename = df.dataframeName
    df = df.dropna('columns') # drop columns with NaN
    df = df[[col for col in df if df[col].nunique() > 1]] # keep columns where there are more than 1 unique values
    if df.shape[1] < 2:
        print(f'No correlation plots shown: The number of non-NaN or constant columns ({df.shape[1]}) is less than 2')
        return
    corr = df.corr()
    plt.figure(num=None, figsize=(graphWidth, graphWidth), dpi=80, facecolor='w', edgecolor='k')
    corrMat = plt.matshow(corr, fignum = 1)
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.gca().xaxis.tick_bottom()
    plt.colorbar(corrMat)
    plt.title(f'Correlation Matrix for {filename}', fontsize=15)
    plt.show()


# In[ ]:


# Scatter and density plots
def plotScatterMatrix(df, plotSize, textSize):
    df = df.select_dtypes(include =[np.number]) # keep only numerical columns
    # Remove rows and columns that would lead to df being singular
    df = df.dropna('columns')
    df = df[[col for col in df if df[col].nunique() > 1]] # keep columns where there are more than 1 unique values
    columnNames = list(df)
    if len(columnNames) > 10: # reduce the number of columns for matrix inversion of kernel density plots
        columnNames = columnNames[:10]
    df = df[columnNames]
    ax = pd.plotting.scatter_matrix(df, alpha=0.75, figsize=[plotSize, plotSize], diagonal='kde')
    corrs = df.corr().values
    for i, j in zip(*plt.np.triu_indices_from(ax, k = 1)):
        ax[i, j].annotate('Corr. coef = %.3f' % corrs[i, j], (0.8, 0.2), xycoords='axes fraction', ha='center', va='center', size=textSize)
    plt.suptitle('Scatter and Density Plot')
    plt.show()


# Now you're ready to read in the data and use the plotting functions to visualize the data.

# ### Let's check 1st file: /kaggle/input/episodes.csv

# In[ ]:


nRowsRead = 1000 # specify 'None' if want to read whole file
# episodes.csv may have more rows in reality, but we are only loading/previewing the first 1000 rows
df1 = pd.read_csv('/kaggle/input/episodes.csv', delimiter=',', nrows = nRowsRead)
df1.dataframeName = 'episodes.csv'
nRow, nCol = df1.shape
print(f'There are {nRow} rows and {nCol} columns')


# Let's take a quick look at what the data looks like:

# In[ ]:


df1.head(5)


# Distribution graphs (histogram/bar graph) of sampled columns:

# In[ ]:


plotPerColumnDistribution(df1, 10, 5)


# ### Let's check 2nd file: /kaggle/input/utterances-2sp.csv

# In[ ]:


nRowsRead = 1000 # specify 'None' if want to read whole file
# utterances-2sp.csv may have more rows in reality, but we are only loading/previewing the first 1000 rows
df2 = pd.read_csv('/kaggle/input/utterances-2sp.csv', delimiter=',', nrows = nRowsRead)
df2.dataframeName = 'utterances-2sp.csv'
nRow, nCol = df2.shape
print(f'There are {nRow} rows and {nCol} columns')


# Let's take a quick look at what the data looks like:

# In[ ]:


df2.head(5)


# Distribution graphs (histogram/bar graph) of sampled columns:

# In[ ]:


plotPerColumnDistribution(df2, 10, 5)


# Correlation matrix:

# In[ ]:


plotCorrelationMatrix(df2, 8)


# Scatter and density plots:

# In[ ]:


plotScatterMatrix(df2, 15, 10)


# ### Let's check 3rd file: /kaggle/input/utterances.csv

# In[ ]:


nRowsRead = 1000 # specify 'None' if want to read whole file
# utterances.csv may have more rows in reality, but we are only loading/previewing the first 1000 rows
df3 = pd.read_csv('/kaggle/input/utterances.csv', delimiter=',', nrows = nRowsRead)
df3.dataframeName = 'utterances.csv'
nRow, nCol = df3.shape
print(f'There are {nRow} rows and {nCol} columns')


# Let's take a quick look at what the data looks like:

# In[ ]:


df3.head(5)


# Distribution graphs (histogram/bar graph) of sampled columns:

# In[ ]:


plotPerColumnDistribution(df3, 10, 5)


# Correlation matrix:

# In[ ]:


plotCorrelationMatrix(df3, 8)


# Scatter and density plots:

# In[ ]:


plotScatterMatrix(df3, 6, 15)


# ## Conclusion
# This concludes your starter analysis! To go forward from here, click the blue "Edit Notebook" button at the top of the kernel. This will create a copy of the code and environment for you to edit. Delete, modify, and add code as you please. Happy Kaggling!

# In[ ]:


import torch
import torch.nn as nn
import pandas as pd
from transformers import GPT2Tokenizer

print('Initialized environment')

# Tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
display(len(tokenizer))

# Experiment with two-speaker utterances
two_speaker_utterances = pd.read_csv('/kaggle/input/interview-npr-media-dialog-transcripts/utterances-2sp.csv', engine='c')
display(two_speaker_utterances.head(3))

# How to run an LSTM language model on a single utterance
embed_dim = 64
hidden_dim = 128
layers = 2

# Vocabulary embedding
embedding = nn.Embedding(
    len(tokenizer), embed_dim
)

# LSTM model
lstm_lm = nn.LSTM(
    input_size=embed_dim,
    hidden_size=hidden_dim,
    num_layers=layers,
    batch_first=True,
    dropout=0.1
)

# Logits projection
logits_proj = nn.Linear(
    hidden_dim, len(tokenizer)
)

print('Created model')

# Batch size of 1, B x T
utterance_ids = torch.LongTensor([tokenizer.encode(two_speaker_utterances.iloc[0]['utterance'], append_prefix_space=False)])
inputs = utterance_ids[:, :-1]
targets = utterance_ids[:, 1:]

# B x T x E
input_emb = embedding(inputs)

# B x T x H
outputs, _ = lstm_lm(input_emb)

# B x T x V
logits = logits_proj(outputs)
display(logits.shape)
