#!/usr/bin/env python
# coding: utf-8

# # Tuned Point to uncertainty - 0. 15 LB 
# 
# If you like it, upvote it. It's right next to "Copy and Edit".
# 
# Forked from https://www.kaggle.com/kneroma/from-point-to-uncertainty-prediction and https://www.kaggle.com/szmnkrisz97/point-to-uncertainty-different-ranges-per-level and in the end tuned by me :)
# 

# In[ ]:


import pandas as pd, numpy as np
from matplotlib import pyplot as plt

import scipy.stats  as stats


# In[ ]:


pd.options.display.max_columns = 50


# In[ ]:


best = pd.read_csv("../input/accuracy-best-public-lbs/kkiller_first_public_notebook_under050_v5.csv")
best.head()


# In[ ]:


sales = pd.read_csv("../input/m5-forecasting-uncertainty/sales_train_validation.csv")
sales.head()


# In[ ]:


sub = best.merge(sales[["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]], on = "id")
sub["_all_"] = "Total"
sub.shape


# In[ ]:


sub.head()


# ## Different ratios for different aggregation levels
# 
# The higher the aggregation level, the more confident we are in the point prediction --> lower coef, relatively smaller range of quantiles

# In[ ]:


qs = np.array([0.005,0.025,0.165,0.25, 0.5, 0.75, 0.835, 0.975, 0.995])
qs.shape


def get_ratios(coef=0.15):
    qs2 = np.log(qs/(1-qs))*coef
    ratios = stats.norm.cdf(qs2)
    ratios /= ratios[4]
    ratios = pd.Series(ratios, index=qs)
    return ratios.round(3)

#coef between 0.05 and 0.24 is used, probably suboptimal values for now

level_coef_dict = {"id": get_ratios(coef=0.17), "item_id": get_ratios(coef=0.10),
                   "dept_id": get_ratios(coef=0.04), "cat_id": get_ratios(coef=0.04),
                   "store_id": get_ratios(coef=0.04), "state_id": get_ratios(coef=0.04), "_all_": get_ratios(coef=0.04),
                   ("state_id", "item_id"): get_ratios(coef=0.12),  ("state_id", "dept_id"): get_ratios(coef=0.08),
                    ("store_id","dept_id") : get_ratios(coef=0.05), ("state_id", "cat_id"): get_ratios(coef=0.06),
                    ("store_id","cat_id"): get_ratios(coef=0.1)
                  }


# Let's see how ranges differ!

# In[ ]:


level_coef_dict["id"]


# In[ ]:


level_coef_dict["cat_id"]


# For the the lowest level (30490 series), the smallest and biggest quantiles are 20% and 180% of the point prediction. For categories (3 series), the model will be way more confident: the smallest quantile will be 71%, the biggest will be 129% of the point prediction.

# In[ ]:




def quantile_coefs(q, level):
    ratios = level_coef_dict[level]
               
    return ratios.loc[q].values

def get_group_preds(pred, level):
    df = pred.groupby(level)[cols].sum()
    q = np.repeat(qs, len(df))
    df = pd.concat([df]*9, axis=0, sort=False)
    df.reset_index(inplace = True)
    df[cols] *= quantile_coefs(q, level)[:, None]
    if level != "id":
        df["id"] = [f"{lev}_X_{q:.3f}_validation" for lev, q in zip(df[level].values, q)]
    else:
        df["id"] = [f"{lev.replace('_validation', '')}_{q:.3f}_validation" for lev, q in zip(df[level].values, q)]
    df = df[["id"]+list(cols)]
    return df

def get_couple_group_preds(pred, level1, level2):
    df = pred.groupby([level1, level2])[cols].sum()
    q = np.repeat(qs, len(df))
    df = pd.concat([df]*9, axis=0, sort=False)
    df.reset_index(inplace = True)
    df[cols] *= quantile_coefs(q, (level1, level2))[:, None]
    df["id"] = [f"{lev1}_{lev2}_{q:.3f}_validation" for lev1,lev2, q in 
                zip(df[level1].values,df[level2].values, q)]
    df = df[["id"]+list(cols)]
    return df

levels = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id", "_all_"]
couples = [("state_id", "item_id"),  ("state_id", "dept_id"),("store_id","dept_id"),
                            ("state_id", "cat_id"),("store_id","cat_id")]
cols = [f"F{i}" for i in range(1, 29)]

df = []
for level in levels :
    df.append(get_group_preds(sub, level))
for level1,level2 in couples:
    df.append(get_couple_group_preds(sub, level1, level2))
df = pd.concat(df, axis=0, sort=False)
df.reset_index(drop=True, inplace=True)
df = pd.concat([df,df] , axis=0, sort=False)
df.reset_index(drop=True, inplace=True)
df.loc[df.index >= len(df.index)//2, "id"] = df.loc[df.index >= len(df.index)//2, "id"].str.replace(
                                    "_validation$", "_evaluation")

df.shape

df.head()

df.to_csv("submission.csv", index = False)
