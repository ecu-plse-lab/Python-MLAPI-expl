# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from matplotlib import pyplot
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

#from subprocess import check_output
#print(check_output(["ls", "../input"]).decode("utf8"))

# Any results you write to the current directory are saved as output.
df = pd.read_csv(r'../input/cps_2016-08.csv')
df = df[['HEFAMINC', 'HRHTYPE', 'HRNUMHOU']]
print(df.head())
df = df[df['HEFAMINC'] >= 1]
inc = df.ix[:, 'HEFAMINC']
print(inc.describe())

# Plot boxplots
box_data_to_plot = [ inc ]
pyplot.figure(1)
label = ['Income']
pyplot.boxplot(box_data_to_plot, labels=label)
pyplot.grid()