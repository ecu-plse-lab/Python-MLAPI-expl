# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

data = pd.read_csv('../input/data.csv');
print(data.iloc[:10, 0])
X = data.iloc[:, 0].values
Y = data.iloc[:, 1].values

foo = plt.plot([5, 6, 7, 8, 9, 10, 11], [5, 6, 7, 8, 9, 10, 11])
plt.show()

# Any results you write to the current directory are saved as output.