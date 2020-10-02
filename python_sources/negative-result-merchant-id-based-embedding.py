#!/usr/bin/env python
# coding: utf-8

# # Objective of the notebook
# 
# The main objective is to show that there is little information in the merchant_id column by itself (in historical_transactions.csv)

# In[ ]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

import os
print(os.listdir("../input"))

# Any results you write to the current directory are saved as output.


# In[ ]:


hist_df = pd.read_csv("../input/historical_transactions.csv")


# In[ ]:


hist_df.head()


# Lets index card_ids and merchant_ids so that we can use matrix methods

# In[ ]:


card_id_to_idx = dict((card_id, i) for i, card_id in enumerate(hist_df["card_id"].unique()))
merchant_id_to_idx = dict((merchant_id, i) for i, merchant_id in enumerate(hist_df["merchant_id"].unique()))


# Place the indexes in two columns of the dataframe

# In[ ]:


hist_df["u"] = hist_df["card_id"].apply(lambda x: card_id_to_idx[x])
hist_df["v"] = hist_df["merchant_id"].apply(lambda x: merchant_id_to_idx[x])


# # Matrix formulation
# Lets see if we get any signal if we draw a graph linking cust_id and merchant_id if there was a purchase
# The matrix **mat** represents the *adjaceny matrix* and **mat_tilde** represents the *normalized adjacency matrix* of this graph

# In[ ]:


import scipy.sparse

m = len(card_id_to_idx)
n = len(merchant_id_to_idx)

u = hist_df["u"].values
v = hist_df["v"].values
w = [1 for _ in u]

mat = scipy.sparse.coo_matrix((w, (u, v)), shape=(m, n)).tocsr()

d1 = np.squeeze(np.sum(mat, axis=1), axis=1).tolist()[0]
d1tilde = [1. / np.sqrt(x) if x > 0 else 0. for x in d1]

d2 = np.squeeze(np.sum(mat, axis=0)).tolist()[0]
d2tilde = [1. / np.sqrt(x) if x > 0 else 0. for x in d2]

def diags(l):
    idx = [i for i in range(len(l))]
    return scipy.sparse.coo_matrix((l, (idx, idx))).tocsr()

mat_tilde = diags(d1tilde).dot(mat).dot(diags(d2tilde))


# # Singular value decomposition of normalized adjacency matrix
# 
# * Lets create features using the left singular values of the *normalized adjacency matix* **mat_tilde**
# * We will use 50 singular vectors

# In[ ]:


import scipy.sparse.linalg

nproj = 50

# proj_mat = np.random.randn(*(n, nproj))
# feat_mat = mat_tilde.dot(proj_mat)
# mat = mat.asfptype()
u, s, vt = scipy.sparse.linalg.svds(mat_tilde, k=nproj)

u.shape, s.shape, vt.shape


# # Lets plot the singular vectors
# * The graph is disconnected with two components (two singular vectors are equal to 1)
# * The other 48 singular vectors should give us a good embedding of card_id if there is one 

# In[ ]:


import matplotlib.pyplot as plt
plt.stem(s)
print(np.sum(s==1))


# # Embedding of card_id using merchant_id s

# In[ ]:


feat_mat = u.dot(np.diag(s))
feat_mat.shape


# In[ ]:


from sklearn.model_selection import train_test_split

df = pd.read_csv("../input/train.csv")
train_df, val_df = train_test_split(df, test_size=0.1, random_state=2018)
test_df = pd.read_csv("../input/test.csv")


# In[ ]:


train_df.head()


# # Use embedding to generate features for train, val and test data

# In[ ]:


def get_labeled_data(df):
    y = None
    
    if "target" in df.columns:
        y = df["target"].values
    
    X = np.zeros((df.shape[0], nproj))
    
    for i, irow in enumerate(df.iterrows()):
        _, row = irow
        idx = card_id_to_idx[row["card_id"]]
        X[i, :] = feat_mat[idx, :]
    
    valid_idx = np.sum(np.abs(X), axis=1) > 0
    
    return X, y, valid_idx


# In[ ]:


train_X, train_y, train_idx = get_labeled_data(train_df)
val_X, val_y, val_idx = get_labeled_data(val_df)
test_X, _, _ = get_labeled_data(test_df)


# In[ ]:


from sklearn.ensemble import GradientBoostingRegressor

model = GradientBoostingRegressor(verbose=2, n_estimators=50)
model.fit(train_X[train_idx, :], train_y[train_idx])


# # We dont improve much over constant predictor

# In[ ]:


print("Preformance improved to {} from the trivial value of {}".format(np.sqrt(np.mean(np.square(model.predict(val_X[val_idx, :]) - val_y[val_idx]))), np.sqrt(np.mean(np.square(np.mean(train_y[train_idx]) - val_y[val_idx])))))


# In[ ]:


pd.DataFrame({
    "card_id": test_df["card_id"],
    "target": model.predict(test_X)
}).to_csv("submission.csv", index=False)
