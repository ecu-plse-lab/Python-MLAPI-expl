#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 5GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# In[ ]:


import torch
import pandas as pd
import numpy as np
import random
import torch.nn.functional as F


# In[ ]:


batch=100
learning_rate=0.001
drop_prob=0.3
width=256


# In[ ]:


train_csv = pd.read_csv('/kaggle/input/tft-hyona/moral_TFT_train.csv')
train_D = train_csv.drop('Ranked',axis = 1)
train_L = train_csv.Ranked
test_D = pd.read_csv('/kaggle/input/tft-hyona/moral_TFT_test.csv')


# In[ ]:


train_D= torch.FloatTensor(np.array(train_D))
train_L = torch.LongTensor(np.array(train_L))
test_D = torch.FloatTensor(np.array(test_D))


# In[ ]:


data_loader = torch.utils.data.DataLoader(dataset=torch.utils.data.TensorDataset(train_D, train_L),
                                          batch_size=batch,
                                          shuffle=True,
                                          drop_last=True)


# In[ ]:


linear1= torch.nn.Linear(train_D.shape[1], width, bias = True)
linear2 = torch.nn.Linear(width,width,bias = True)
linear3 = torch.nn.Linear(256,256,bias = True)
linear4 = torch.nn.Linear(256,256,bias = True)
linear5 = torch.nn.Linear(256,2, bias=  True)
relu = torch.nn.PReLU()
dropout = torch.nn.Dropout(p = drop_prob)


# In[ ]:


torch.nn.init.xavier_uniform_(linear1.weight)
torch.nn.init.xavier_uniform_(linear2.weight)
torch.nn.init.xavier_uniform_(linear3.weight)
torch.nn.init.xavier_uniform_(linear4.weight)
torch.nn.init.xavier_uniform_(linear5.weight)


# In[ ]:


device = 'cuda' if torch.cuda.is_available() else 'cpu'

random.seed(777)
torch.manual_seed(777)
if device == 'cuda':
  torch.cuda.manual_seed_all(777)


# In[ ]:


model = torch.nn.Sequential(linear1, relu, dropout,
                            linear2, relu, dropout,
                            linear3, relu, dropout,
                            linear4, relu, dropout,
                            linear5).to(device)


# In[ ]:


loss =torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 0.001)


# In[ ]:


total_batch = len(data_loader)
model.train()
for e in range(22):
  avg_cost= 0
  for x, y in data_loader:
    x = x.to(device)
    y=  y.to(device)
    #print(x.shape)
    optimizer.zero_grad()
    h_x = model(x)
    cost = loss(h_x, y)
    cost.backward()
    optimizer.step()
    avg_cost += cost / total_batch
  print('Epoch {}'.format(e), 'cost {}'.format(avg_cost))


# In[ ]:


test_D = torch.FloatTensor(np.array(test_D))


# In[ ]:


with torch.no_grad():
  model.eval()
  pred=  model(test_D.to(device))


# In[ ]:


result = pd.read_csv('/kaggle/input/tft-hyona/sample.csv')
result = result.drop("Unnamed: 0",1)
result


# In[ ]:


result['id'] = list(i for i in range(3300))
result['result'] = torch.argmax(pred, 1).cpu()
result


# In[ ]:


result.to_csv('submission.csv', index = False)


# In[ ]:



