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
        

import time
import nltk, string
import random
from nltk.corpus import stopwords 
from nltk.stem import WordNetLemmatizer

pd.options.display.max_colwidth = -1


# df=pd.read_csv('/kaggle/input/CORD-19-research-challenge/metadata.csv')
# print (df.shape)
#4/3/20 47298,18
#print ('end script')