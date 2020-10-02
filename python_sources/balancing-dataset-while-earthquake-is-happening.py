#!/usr/bin/env python
# coding: utf-8

# ## Datasest Is Not Even, Let's Balance
# 
# ![](https://images.unsplash.com/photo-1502489825135-69dbb92e42ea?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=3900&q=80)
# (Photo from https://unsplash.com/photos/h6zMgghzZr0)
# 
# As you might walk through some kernels, and might have found that many results:
# - Predict well with the middle ranged results.
# - Are hard to predict higher value (longer time to failure) results.
# 
# This would simply be caused by the distribution bias of the dataset. This kernel shows:
# - How is the distribution of the training data.
# - How to resample.
# - Result after resampling to make the distribution even.
# 
# And this kernel is forked from Andrew's ['Earthquakes FE. More features and samples'](https://www.kaggle.com/artgor/earthquakes-fe-more-features-and-samples). Thank you, [Andrew](https://www.kaggle.com/artgor).
# 
# *Disclaimer: This kernel shows that dataset can be balanced, but does not provide complete solution.*

# In[ ]:


import numpy as np
import pandas as pd
import os

import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
from tqdm import tqdm_notebook
from sklearn.preprocessing import StandardScaler
from sklearn.svm import NuSVR, SVR
from sklearn.metrics import mean_absolute_error
pd.options.display.precision = 15

import lightgbm as lgb
import xgboost as xgb
import time
import datetime
from catboost import CatBoostRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, KFold, RepeatedKFold
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression
import gc
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

from scipy.signal import hilbert
from scipy.signal import hann
from scipy.signal import convolve
from scipy import stats
from sklearn.kernel_ridge import KernelRidge


# ## Skipping basics: load dataset and do the FE

# In[ ]:


get_ipython().run_cell_magic('time', '', 'train = pd.read_csv(\'../input/train.csv\', dtype={\'acoustic_data\': np.int16, \'time_to_failure\': np.float32})\n\ntrain_acoustic_data_small = train[\'acoustic_data\'].values[::50]\ntrain_time_to_failure_small = train[\'time_to_failure\'].values[::50]\n\nfig, ax1 = plt.subplots(figsize=(16, 8))\nplt.title("Trends of acoustic_data and time_to_failure. 2% of data (sampled)")\nplt.plot(train_acoustic_data_small, color=\'b\')\nax1.set_ylabel(\'acoustic_data\', color=\'b\')\nplt.legend([\'acoustic_data\'])\nax2 = ax1.twinx()\nplt.plot(train_time_to_failure_small, color=\'g\')\nax2.set_ylabel(\'time_to_failure\', color=\'g\')\nplt.legend([\'time_to_failure\'], loc=(0.875, 0.9))\nplt.grid(False)\n\ndel train_acoustic_data_small\ndel train_time_to_failure_small\n\n# Create a training file with simple derived features\nrows = 150_000\nsegments = int(np.floor(train.shape[0] / rows))\n\ndef add_trend_feature(arr, abs_values=False):\n    idx = np.array(range(len(arr)))\n    if abs_values:\n        arr = np.abs(arr)\n    lr = LinearRegression()\n    lr.fit(idx.reshape(-1, 1), arr)\n    return lr.coef_[0]\n\ndef classic_sta_lta(x, length_sta, length_lta):\n    \n    sta = np.cumsum(x ** 2)\n\n    # Convert to float\n    sta = np.require(sta, dtype=np.float)\n\n    # Copy for LTA\n    lta = sta.copy()\n\n    # Compute the STA and the LTA\n    sta[length_sta:] = sta[length_sta:] - sta[:-length_sta]\n    sta /= length_sta\n    lta[length_lta:] = lta[length_lta:] - lta[:-length_lta]\n    lta /= length_lta\n\n    # Pad zeros\n    sta[:length_lta - 1] = 0\n\n    # Avoid division by zero by setting zero values to tiny float\n    dtiny = np.finfo(0.0).tiny\n    idx = lta < dtiny\n    lta[idx] = dtiny\n\n    return sta / lta\n\nX_tr = pd.DataFrame(index=range(segments), dtype=np.float64)\n\ny_tr = pd.DataFrame(index=range(segments), dtype=np.float64, columns=[\'time_to_failure\'])\n\ntotal_mean = train[\'acoustic_data\'].mean()\ntotal_std = train[\'acoustic_data\'].std()\ntotal_max = train[\'acoustic_data\'].max()\ntotal_min = train[\'acoustic_data\'].min()\ntotal_sum = train[\'acoustic_data\'].sum()\ntotal_abs_sum = np.abs(train[\'acoustic_data\']).sum()\n\ndef calc_change_rate(x):\n    change = (np.diff(x) / x[:-1]).values\n    change = change[np.nonzero(change)[0]]\n    change = change[~np.isnan(change)]\n    change = change[change != -np.inf]\n    change = change[change != np.inf]\n    return np.mean(change)\n\nfor segment in tqdm_notebook(range(segments)):\n    seg = train.iloc[segment*rows:segment*rows+rows]\n    x = pd.Series(seg[\'acoustic_data\'].values)\n    y = seg[\'time_to_failure\'].values[-1]\n    \n    y_tr.loc[segment, \'time_to_failure\'] = y\n    X_tr.loc[segment, \'mean\'] = x.mean()\n    X_tr.loc[segment, \'std\'] = x.std()\n    X_tr.loc[segment, \'max\'] = x.max()\n    X_tr.loc[segment, \'min\'] = x.min()\n    \n    X_tr.loc[segment, \'mean_change_abs\'] = np.mean(np.diff(x))\n    X_tr.loc[segment, \'mean_change_rate\'] = calc_change_rate(x)\n    X_tr.loc[segment, \'abs_max\'] = np.abs(x).max()\n    X_tr.loc[segment, \'abs_min\'] = np.abs(x).min()\n    \n    X_tr.loc[segment, \'std_first_50000\'] = x[:50000].std()\n    X_tr.loc[segment, \'std_last_50000\'] = x[-50000:].std()\n    X_tr.loc[segment, \'std_first_10000\'] = x[:10000].std()\n    X_tr.loc[segment, \'std_last_10000\'] = x[-10000:].std()\n    \n    X_tr.loc[segment, \'avg_first_50000\'] = x[:50000].mean()\n    X_tr.loc[segment, \'avg_last_50000\'] = x[-50000:].mean()\n    X_tr.loc[segment, \'avg_first_10000\'] = x[:10000].mean()\n    X_tr.loc[segment, \'avg_last_10000\'] = x[-10000:].mean()\n    \n    X_tr.loc[segment, \'min_first_50000\'] = x[:50000].min()\n    X_tr.loc[segment, \'min_last_50000\'] = x[-50000:].min()\n    X_tr.loc[segment, \'min_first_10000\'] = x[:10000].min()\n    X_tr.loc[segment, \'min_last_10000\'] = x[-10000:].min()\n    \n    X_tr.loc[segment, \'max_first_50000\'] = x[:50000].max()\n    X_tr.loc[segment, \'max_last_50000\'] = x[-50000:].max()\n    X_tr.loc[segment, \'max_first_10000\'] = x[:10000].max()\n    X_tr.loc[segment, \'max_last_10000\'] = x[-10000:].max()\n    \n    X_tr.loc[segment, \'max_to_min\'] = x.max() / np.abs(x.min())\n    X_tr.loc[segment, \'max_to_min_diff\'] = x.max() - np.abs(x.min())\n    X_tr.loc[segment, \'count_big\'] = len(x[np.abs(x) > 500])\n    X_tr.loc[segment, \'sum\'] = x.sum()\n    \n    X_tr.loc[segment, \'mean_change_rate_first_50000\'] = calc_change_rate(x[:50000])\n    X_tr.loc[segment, \'mean_change_rate_last_50000\'] = calc_change_rate(x[-50000:])\n    X_tr.loc[segment, \'mean_change_rate_first_10000\'] = calc_change_rate(x[:10000])\n    X_tr.loc[segment, \'mean_change_rate_last_10000\'] = calc_change_rate(x[-10000:])\n    \n    X_tr.loc[segment, \'q95\'] = np.quantile(x, 0.95)\n    X_tr.loc[segment, \'q99\'] = np.quantile(x, 0.99)\n    X_tr.loc[segment, \'q05\'] = np.quantile(x, 0.05)\n    X_tr.loc[segment, \'q01\'] = np.quantile(x, 0.01)\n    \n    X_tr.loc[segment, \'abs_q95\'] = np.quantile(np.abs(x), 0.95)\n    X_tr.loc[segment, \'abs_q99\'] = np.quantile(np.abs(x), 0.99)\n    X_tr.loc[segment, \'abs_q05\'] = np.quantile(np.abs(x), 0.05)\n    X_tr.loc[segment, \'abs_q01\'] = np.quantile(np.abs(x), 0.01)\n    \n    X_tr.loc[segment, \'trend\'] = add_trend_feature(x)\n    X_tr.loc[segment, \'abs_trend\'] = add_trend_feature(x, abs_values=True)\n    X_tr.loc[segment, \'abs_mean\'] = np.abs(x).mean()\n    X_tr.loc[segment, \'abs_std\'] = np.abs(x).std()\n    \n    X_tr.loc[segment, \'mad\'] = x.mad()\n    X_tr.loc[segment, \'kurt\'] = x.kurtosis()\n    X_tr.loc[segment, \'skew\'] = x.skew()\n    X_tr.loc[segment, \'med\'] = x.median()\n    \n    X_tr.loc[segment, \'Hilbert_mean\'] = np.abs(hilbert(x)).mean()\n    X_tr.loc[segment, \'Hann_window_mean\'] = (convolve(x, hann(150), mode=\'same\') / sum(hann(150))).mean()\n    X_tr.loc[segment, \'classic_sta_lta1_mean\'] = classic_sta_lta(x, 500, 10000).mean()\n    X_tr.loc[segment, \'classic_sta_lta2_mean\'] = classic_sta_lta(x, 5000, 100000).mean()\n    X_tr.loc[segment, \'classic_sta_lta3_mean\'] = classic_sta_lta(x, 3333, 6666).mean()\n    X_tr.loc[segment, \'classic_sta_lta4_mean\'] = classic_sta_lta(x, 10000, 25000).mean()\n    X_tr.loc[segment, \'classic_sta_lta5_mean\'] = classic_sta_lta(x, 50, 1000).mean()\n    X_tr.loc[segment, \'classic_sta_lta6_mean\'] = classic_sta_lta(x, 100, 5000).mean()\n    X_tr.loc[segment, \'classic_sta_lta7_mean\'] = classic_sta_lta(x, 333, 666).mean()\n    X_tr.loc[segment, \'classic_sta_lta8_mean\'] = classic_sta_lta(x, 4000, 10000).mean()\n    X_tr.loc[segment, \'Moving_average_700_mean\'] = x.rolling(window=700).mean().mean(skipna=True)\n    ewma = pd.Series.ewm\n    X_tr.loc[segment, \'exp_Moving_average_300_mean\'] = (ewma(x, span=300).mean()).mean(skipna=True)\n    X_tr.loc[segment, \'exp_Moving_average_3000_mean\'] = ewma(x, span=3000).mean().mean(skipna=True)\n    X_tr.loc[segment, \'exp_Moving_average_30000_mean\'] = ewma(x, span=30000).mean().mean(skipna=True)\n    no_of_std = 3\n    X_tr.loc[segment, \'MA_700MA_std_mean\'] = x.rolling(window=700).std().mean()\n    X_tr.loc[segment,\'MA_700MA_BB_high_mean\'] = (X_tr.loc[segment, \'Moving_average_700_mean\'] + no_of_std * X_tr.loc[segment, \'MA_700MA_std_mean\']).mean()\n    X_tr.loc[segment,\'MA_700MA_BB_low_mean\'] = (X_tr.loc[segment, \'Moving_average_700_mean\'] - no_of_std * X_tr.loc[segment, \'MA_700MA_std_mean\']).mean()\n    X_tr.loc[segment, \'MA_400MA_std_mean\'] = x.rolling(window=400).std().mean()\n    X_tr.loc[segment,\'MA_400MA_BB_high_mean\'] = (X_tr.loc[segment, \'Moving_average_700_mean\'] + no_of_std * X_tr.loc[segment, \'MA_400MA_std_mean\']).mean()\n    X_tr.loc[segment,\'MA_400MA_BB_low_mean\'] = (X_tr.loc[segment, \'Moving_average_700_mean\'] - no_of_std * X_tr.loc[segment, \'MA_400MA_std_mean\']).mean()\n    X_tr.loc[segment, \'MA_1000MA_std_mean\'] = x.rolling(window=1000).std().mean()\n    X_tr.drop(\'Moving_average_700_mean\', axis=1, inplace=True)\n    \n    X_tr.loc[segment, \'iqr\'] = np.subtract(*np.percentile(x, [75, 25]))\n    X_tr.loc[segment, \'q999\'] = np.quantile(x,0.999)\n    X_tr.loc[segment, \'q001\'] = np.quantile(x,0.001)\n    X_tr.loc[segment, \'ave10\'] = stats.trim_mean(x, 0.1)\n\n    for windows in [10, 100, 1000]:\n        x_roll_std = x.rolling(windows).std().dropna().values\n        x_roll_mean = x.rolling(windows).mean().dropna().values\n        \n        X_tr.loc[segment, \'ave_roll_std_\' + str(windows)] = x_roll_std.mean()\n        X_tr.loc[segment, \'std_roll_std_\' + str(windows)] = x_roll_std.std()\n        X_tr.loc[segment, \'max_roll_std_\' + str(windows)] = x_roll_std.max()\n        X_tr.loc[segment, \'min_roll_std_\' + str(windows)] = x_roll_std.min()\n        X_tr.loc[segment, \'q01_roll_std_\' + str(windows)] = np.quantile(x_roll_std, 0.01)\n        X_tr.loc[segment, \'q05_roll_std_\' + str(windows)] = np.quantile(x_roll_std, 0.05)\n        X_tr.loc[segment, \'q95_roll_std_\' + str(windows)] = np.quantile(x_roll_std, 0.95)\n        X_tr.loc[segment, \'q99_roll_std_\' + str(windows)] = np.quantile(x_roll_std, 0.99)\n        X_tr.loc[segment, \'av_change_abs_roll_std_\' + str(windows)] = np.mean(np.diff(x_roll_std))\n        X_tr.loc[segment, \'av_change_rate_roll_std_\' + str(windows)] = np.mean(np.nonzero((np.diff(x_roll_std) / x_roll_std[:-1]))[0])\n        X_tr.loc[segment, \'abs_max_roll_std_\' + str(windows)] = np.abs(x_roll_std).max()\n        \n        X_tr.loc[segment, \'ave_roll_mean_\' + str(windows)] = x_roll_mean.mean()\n        X_tr.loc[segment, \'std_roll_mean_\' + str(windows)] = x_roll_mean.std()\n        X_tr.loc[segment, \'max_roll_mean_\' + str(windows)] = x_roll_mean.max()\n        X_tr.loc[segment, \'min_roll_mean_\' + str(windows)] = x_roll_mean.min()\n        X_tr.loc[segment, \'q01_roll_mean_\' + str(windows)] = np.quantile(x_roll_mean, 0.01)\n        X_tr.loc[segment, \'q05_roll_mean_\' + str(windows)] = np.quantile(x_roll_mean, 0.05)\n        X_tr.loc[segment, \'q95_roll_mean_\' + str(windows)] = np.quantile(x_roll_mean, 0.95)\n        X_tr.loc[segment, \'q99_roll_mean_\' + str(windows)] = np.quantile(x_roll_mean, 0.99)\n        X_tr.loc[segment, \'av_change_abs_roll_mean_\' + str(windows)] = np.mean(np.diff(x_roll_mean))\n        X_tr.loc[segment, \'av_change_rate_roll_mean_\' + str(windows)] = np.mean(np.nonzero((np.diff(x_roll_mean) / x_roll_mean[:-1]))[0])\n        X_tr.loc[segment, \'abs_max_roll_mean_\' + str(windows)] = np.abs(x_roll_mean).max()\n\nprint(f\'{X_tr.shape[0]} samples in new train data and {X_tr.shape[1]} columns.\')\n\nplt.figure(figsize=(44, 24))\ncols = list(np.abs(X_tr.corrwith(y_tr[\'time_to_failure\'])).sort_values(ascending=False).head(24).index)\nfor i, col in enumerate(cols):\n    plt.subplot(6, 4, i + 1)\n    plt.plot(X_tr[col], color=\'blue\')\n    plt.title(col)\n    ax1.set_ylabel(col, color=\'b\')\n\n    ax2 = ax1.twinx()\n    plt.plot(y_tr, color=\'g\')\n    ax2.set_ylabel(\'time_to_failure\', color=\'g\')\n    plt.legend([col, \'time_to_failure\'], loc=(0.875, 0.9))\n    plt.grid(False)\n\nmeans_dict = {}\nfor col in X_tr.columns:\n    if X_tr[col].isnull().any():\n        print(col)\n        mean_value = X_tr.loc[X_tr[col] != -np.inf, col].mean()\n        X_tr.loc[X_tr[col] == -np.inf, col] = mean_value\n        X_tr[col] = X_tr[col].fillna(mean_value)\n        means_dict[col] = mean_value\n\nscaler = StandardScaler()\nscaler.fit(X_tr)\nX_train_scaled = pd.DataFrame(scaler.transform(X_tr), columns=X_tr.columns)')


# In[ ]:


submission = pd.read_csv('../input/sample_submission.csv', index_col='seg_id')
X_test = pd.DataFrame(columns=X_tr.columns, dtype=np.float64, index=submission.index)
plt.figure(figsize=(22, 16))

for i, seg_id in enumerate(tqdm_notebook(X_test.index)):
    seg = pd.read_csv('../input/test/' + seg_id + '.csv')
    
    x = pd.Series(seg['acoustic_data'].values)
    X_test.loc[seg_id, 'mean'] = x.mean()
    X_test.loc[seg_id, 'std'] = x.std()
    X_test.loc[seg_id, 'max'] = x.max()
    X_test.loc[seg_id, 'min'] = x.min()
        
    X_test.loc[seg_id, 'mean_change_abs'] = np.mean(np.diff(x))
    X_test.loc[seg_id, 'mean_change_rate'] = calc_change_rate(x)
    X_test.loc[seg_id, 'abs_max'] = np.abs(x).max()
    X_test.loc[seg_id, 'abs_min'] = np.abs(x).min()
    
    X_test.loc[seg_id, 'std_first_50000'] = x[:50000].std()
    X_test.loc[seg_id, 'std_last_50000'] = x[-50000:].std()
    X_test.loc[seg_id, 'std_first_10000'] = x[:10000].std()
    X_test.loc[seg_id, 'std_last_10000'] = x[-10000:].std()
    
    X_test.loc[seg_id, 'avg_first_50000'] = x[:50000].mean()
    X_test.loc[seg_id, 'avg_last_50000'] = x[-50000:].mean()
    X_test.loc[seg_id, 'avg_first_10000'] = x[:10000].mean()
    X_test.loc[seg_id, 'avg_last_10000'] = x[-10000:].mean()
    
    X_test.loc[seg_id, 'min_first_50000'] = x[:50000].min()
    X_test.loc[seg_id, 'min_last_50000'] = x[-50000:].min()
    X_test.loc[seg_id, 'min_first_10000'] = x[:10000].min()
    X_test.loc[seg_id, 'min_last_10000'] = x[-10000:].min()
    
    X_test.loc[seg_id, 'max_first_50000'] = x[:50000].max()
    X_test.loc[seg_id, 'max_last_50000'] = x[-50000:].max()
    X_test.loc[seg_id, 'max_first_10000'] = x[:10000].max()
    X_test.loc[seg_id, 'max_last_10000'] = x[-10000:].max()
    
    X_test.loc[seg_id, 'max_to_min'] = x.max() / np.abs(x.min())
    X_test.loc[seg_id, 'max_to_min_diff'] = x.max() - np.abs(x.min())
    X_test.loc[seg_id, 'count_big'] = len(x[np.abs(x) > 500])
    X_test.loc[seg_id, 'sum'] = x.sum()
    
    X_test.loc[seg_id, 'mean_change_rate_first_50000'] = calc_change_rate(x[:50000])
    X_test.loc[seg_id, 'mean_change_rate_last_50000'] = calc_change_rate(x[-50000:])
    X_test.loc[seg_id, 'mean_change_rate_first_10000'] = calc_change_rate(x[:10000])
    X_test.loc[seg_id, 'mean_change_rate_last_10000'] = calc_change_rate(x[-10000:])
    
    X_test.loc[seg_id, 'q95'] = np.quantile(x,0.95)
    X_test.loc[seg_id, 'q99'] = np.quantile(x,0.99)
    X_test.loc[seg_id, 'q05'] = np.quantile(x,0.05)
    X_test.loc[seg_id, 'q01'] = np.quantile(x,0.01)
    
    X_test.loc[seg_id, 'abs_q95'] = np.quantile(np.abs(x), 0.95)
    X_test.loc[seg_id, 'abs_q99'] = np.quantile(np.abs(x), 0.99)
    X_test.loc[seg_id, 'abs_q05'] = np.quantile(np.abs(x), 0.05)
    X_test.loc[seg_id, 'abs_q01'] = np.quantile(np.abs(x), 0.01)
    
    X_test.loc[seg_id, 'trend'] = add_trend_feature(x)
    X_test.loc[seg_id, 'abs_trend'] = add_trend_feature(x, abs_values=True)
    X_test.loc[seg_id, 'abs_mean'] = np.abs(x).mean()
    X_test.loc[seg_id, 'abs_std'] = np.abs(x).std()
    
    X_test.loc[seg_id, 'mad'] = x.mad()
    X_test.loc[seg_id, 'kurt'] = x.kurtosis()
    X_test.loc[seg_id, 'skew'] = x.skew()
    X_test.loc[seg_id, 'med'] = x.median()
    
    X_test.loc[seg_id, 'Hilbert_mean'] = np.abs(hilbert(x)).mean()
    X_test.loc[seg_id, 'Hann_window_mean'] = (convolve(x, hann(150), mode='same') / sum(hann(150))).mean()
    X_test.loc[seg_id, 'classic_sta_lta1_mean'] = classic_sta_lta(x, 500, 10000).mean()
    X_test.loc[seg_id, 'classic_sta_lta2_mean'] = classic_sta_lta(x, 5000, 100000).mean()
    X_test.loc[seg_id, 'classic_sta_lta3_mean'] = classic_sta_lta(x, 3333, 6666).mean()
    X_test.loc[seg_id, 'classic_sta_lta4_mean'] = classic_sta_lta(x, 10000, 25000).mean()
    X_test.loc[seg_id, 'classic_sta_lta5_mean'] = classic_sta_lta(x, 50, 1000).mean()
    X_test.loc[seg_id, 'classic_sta_lta6_mean'] = classic_sta_lta(x, 100, 5000).mean()
    X_test.loc[seg_id, 'classic_sta_lta7_mean'] = classic_sta_lta(x, 333, 666).mean()
    X_test.loc[seg_id, 'classic_sta_lta8_mean'] = classic_sta_lta(x, 4000, 10000).mean()
    X_test.loc[seg_id, 'Moving_average_700_mean'] = x.rolling(window=700).mean().mean(skipna=True)
    ewma = pd.Series.ewm
    X_test.loc[seg_id, 'exp_Moving_average_300_mean'] = (ewma(x, span=300).mean()).mean(skipna=True)
    X_test.loc[seg_id, 'exp_Moving_average_3000_mean'] = ewma(x, span=3000).mean().mean(skipna=True)
    X_test.loc[seg_id, 'exp_Moving_average_30000_mean'] = ewma(x, span=30000).mean().mean(skipna=True)
    no_of_std = 3
    X_test.loc[seg_id, 'MA_700MA_std_mean'] = x.rolling(window=700).std().mean()
    X_test.loc[seg_id,'MA_700MA_BB_high_mean'] = (X_test.loc[seg_id, 'Moving_average_700_mean'] + no_of_std * X_test.loc[seg_id, 'MA_700MA_std_mean']).mean()
    X_test.loc[seg_id,'MA_700MA_BB_low_mean'] = (X_test.loc[seg_id, 'Moving_average_700_mean'] - no_of_std * X_test.loc[seg_id, 'MA_700MA_std_mean']).mean()
    X_test.loc[seg_id, 'MA_400MA_std_mean'] = x.rolling(window=400).std().mean()
    X_test.loc[seg_id,'MA_400MA_BB_high_mean'] = (X_test.loc[seg_id, 'Moving_average_700_mean'] + no_of_std * X_test.loc[seg_id, 'MA_400MA_std_mean']).mean()
    X_test.loc[seg_id,'MA_400MA_BB_low_mean'] = (X_test.loc[seg_id, 'Moving_average_700_mean'] - no_of_std * X_test.loc[seg_id, 'MA_400MA_std_mean']).mean()
    X_test.loc[seg_id, 'MA_1000MA_std_mean'] = x.rolling(window=1000).std().mean()
    X_test.drop('Moving_average_700_mean', axis=1, inplace=True)
    
    X_test.loc[seg_id, 'iqr'] = np.subtract(*np.percentile(x, [75, 25]))
    X_test.loc[seg_id, 'q999'] = np.quantile(x,0.999)
    X_test.loc[seg_id, 'q001'] = np.quantile(x,0.001)
    X_test.loc[seg_id, 'ave10'] = stats.trim_mean(x, 0.1)
    
    for windows in [10, 100, 1000]:
        x_roll_std = x.rolling(windows).std().dropna().values
        x_roll_mean = x.rolling(windows).mean().dropna().values
        
        X_test.loc[seg_id, 'ave_roll_std_' + str(windows)] = x_roll_std.mean()
        X_test.loc[seg_id, 'std_roll_std_' + str(windows)] = x_roll_std.std()
        X_test.loc[seg_id, 'max_roll_std_' + str(windows)] = x_roll_std.max()
        X_test.loc[seg_id, 'min_roll_std_' + str(windows)] = x_roll_std.min()
        X_test.loc[seg_id, 'q01_roll_std_' + str(windows)] = np.quantile(x_roll_std, 0.01)
        X_test.loc[seg_id, 'q05_roll_std_' + str(windows)] = np.quantile(x_roll_std, 0.05)
        X_test.loc[seg_id, 'q95_roll_std_' + str(windows)] = np.quantile(x_roll_std, 0.95)
        X_test.loc[seg_id, 'q99_roll_std_' + str(windows)] = np.quantile(x_roll_std, 0.99)
        X_test.loc[seg_id, 'av_change_abs_roll_std_' + str(windows)] = np.mean(np.diff(x_roll_std))
        X_test.loc[seg_id, 'av_change_rate_roll_std_' + str(windows)] = np.mean(np.nonzero((np.diff(x_roll_std) / x_roll_std[:-1]))[0])
        X_test.loc[seg_id, 'abs_max_roll_std_' + str(windows)] = np.abs(x_roll_std).max()
        
        X_test.loc[seg_id, 'ave_roll_mean_' + str(windows)] = x_roll_mean.mean()
        X_test.loc[seg_id, 'std_roll_mean_' + str(windows)] = x_roll_mean.std()
        X_test.loc[seg_id, 'max_roll_mean_' + str(windows)] = x_roll_mean.max()
        X_test.loc[seg_id, 'min_roll_mean_' + str(windows)] = x_roll_mean.min()
        X_test.loc[seg_id, 'q01_roll_mean_' + str(windows)] = np.quantile(x_roll_mean, 0.01)
        X_test.loc[seg_id, 'q05_roll_mean_' + str(windows)] = np.quantile(x_roll_mean, 0.05)
        X_test.loc[seg_id, 'q95_roll_mean_' + str(windows)] = np.quantile(x_roll_mean, 0.95)
        X_test.loc[seg_id, 'q99_roll_mean_' + str(windows)] = np.quantile(x_roll_mean, 0.99)
        X_test.loc[seg_id, 'av_change_abs_roll_mean_' + str(windows)] = np.mean(np.diff(x_roll_mean))
        X_test.loc[seg_id, 'av_change_rate_roll_mean_' + str(windows)] = np.mean(np.nonzero((np.diff(x_roll_mean) / x_roll_mean[:-1]))[0])
        X_test.loc[seg_id, 'abs_max_roll_mean_' + str(windows)] = np.abs(x_roll_mean).max()
    
    if i < 12:
        plt.subplot(6, 4, i + 1)
        plt.plot(seg['acoustic_data'])
        plt.title(seg_id)

for col in X_test.columns:
    if X_test[col].isnull().any():
        X_test.loc[X_test[col] == -np.inf, col] = means_dict[col]
        X_test[col] = X_test[col].fillna(means_dict[col])
        
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)


# ## Original Data Distribution
# 
# Target value is continuous, ranging from 0 to about 16 seconds. Then let's simply put them in 17 bins by making `time_to_failure` as `int`.

# In[ ]:


# Copying from my repository: https://github.com/daisukelab/dl-cliche

def flatten_y_if_onehot(y):
    """De-one-hot y, i.e. [0,1,0,0,...] to 1 for all y."""
    return y if len(np.array(y).shape) == 1 else np.argmax(y, axis = -1)

def get_class_distribution(y):
    """Calculate number of samples per class."""
    # y_cls can be one of [OH label, index of class, class label name string]
    # convert OH to index of class
    y_cls = flatten_y_if_onehot(y)
    # y_cls can be one of [index of class, class label name]
    classset = sorted(list(set(y_cls)))
    sample_distribution = {cur_cls:len([one for one in y_cls if one == cur_cls]) for cur_cls in classset}
    return sample_distribution

def get_class_distribution_list(y, num_classes):
    """Calculate number of samples per class as list"""
    dist = get_class_distribution(y)
    assert(y[0].__class__ != str) # class index or class OH label only
    list_dist = np.zeros((num_classes))
    for i in range(num_classes):
        if i in dist:
            list_dist[i] = dist[i]
    return list_dist

def _expand_labels_from_y(y, labels):
    """Make sure y is index of label set."""
    if labels is None:
        labels = sorted(list(set(y)))
        y = [labels.index(_y) for _y in y]
    return y, labels

def visualize_class_balance(title, y, labels=None, sorted=False):
    y, labels = _expand_labels_from_y(y, labels)
    sample_dist_list = get_class_distribution_list(y, len(labels))
    if sorted:
        items = list(zip(labels, sample_dist_list))
        items.sort(key=lambda x:x[1], reverse=True)
        sample_dist_list = [x[1] for x in items]
        labels = [x[0] for x in items]
    index = range(len(labels))
    fig, ax = plt.subplots(1, 1, figsize = (16, 5))
    ax.bar(index, sample_dist_list)
    ax.set_xlabel('Label')
    ax.set_xticks(index)
    ax.set_xticklabels(labels, rotation='vertical')
    ax.set_ylabel('Number of Samples')
    ax.set_title(title)
    fig.show()


# In[ ]:


visualize_class_balance('y_tr distribution as is', y_tr.time_to_failure.map(int))


# ## Build Models As Is
# 
# - As you can see the results, model cannot work well with higher value results.
# - LightGBM is used as model type throughout this kernel.

# In[ ]:


n_fold = 5
folds = KFold(n_splits=n_fold, shuffle=True, random_state=11)

def train_model(X=X_train_scaled, X_test=X_test_scaled, y=y_tr, params=None, folds=folds, model_type='lgb', plot_feature_importance=False, model=None):

    oof = np.zeros(len(X))
    prediction = np.zeros(len(X_test))
    scores = []
    feature_importance = pd.DataFrame()
    for fold_n, (train_index, valid_index) in enumerate(folds.split(X)):
        print('Fold', fold_n, 'started at', time.ctime())
        X_train, X_valid = X.iloc[train_index], X.iloc[valid_index]
        y_train, y_valid = y.iloc[train_index], y.iloc[valid_index]
        
        if model_type == 'lgb':
            model = lgb.LGBMRegressor(**params, n_estimators = 50000, n_jobs = -1)
            model.fit(X_train, y_train, 
                    eval_set=[(X_train, y_train), (X_valid, y_valid)], eval_metric='mae',
                    verbose=10000, early_stopping_rounds=200)
            
            y_pred_valid = model.predict(X_valid)
            y_pred = model.predict(X_test, num_iteration=model.best_iteration_)
            
        if model_type == 'xgb':
            train_data = xgb.DMatrix(data=X_train, label=y_train, feature_names=X.columns)
            valid_data = xgb.DMatrix(data=X_valid, label=y_valid, feature_names=X.columns)

            watchlist = [(train_data, 'train'), (valid_data, 'valid_data')]
            model = xgb.train(dtrain=train_data, num_boost_round=20000, evals=watchlist, early_stopping_rounds=200, verbose_eval=500, params=params)
            y_pred_valid = model.predict(xgb.DMatrix(X_valid, feature_names=X.columns), ntree_limit=model.best_ntree_limit)
            y_pred = model.predict(xgb.DMatrix(X_test, feature_names=X.columns), ntree_limit=model.best_ntree_limit)
        
        if model_type == 'sklearn':
            model = model
            model.fit(X_train, y_train)
            
            y_pred_valid = model.predict(X_valid).reshape(-1,)
            score = mean_absolute_error(y_valid, y_pred_valid)
            print(f'Fold {fold_n}. MAE: {score:.4f}.')
            print('')
            
            y_pred = model.predict(X_test).reshape(-1,)
        
        if model_type == 'cat':
            model = CatBoostRegressor(iterations=20000,  eval_metric='MAE', **params)
            model.fit(X_train, y_train, eval_set=(X_valid, y_valid), cat_features=[], use_best_model=True, verbose=False)

            y_pred_valid = model.predict(X_valid)
            y_pred = model.predict(X_test)
        
        oof[valid_index] = y_pred_valid.reshape(-1,)
        scores.append(mean_absolute_error(y_valid, y_pred_valid))

        prediction += y_pred    
        
        if model_type == 'lgb':
            # feature importance
            fold_importance = pd.DataFrame()
            fold_importance["feature"] = X.columns
            fold_importance["importance"] = model.feature_importances_
            fold_importance["fold"] = fold_n + 1
            feature_importance = pd.concat([feature_importance, fold_importance], axis=0)

    prediction /= n_fold
    
    print('CV mean score: {0:.4f}, std: {1:.4f}.'.format(np.mean(scores), np.std(scores)))
    
    if model_type == 'lgb':
        feature_importance["importance"] /= n_fold
        if plot_feature_importance:
            cols = feature_importance[["feature", "importance"]].groupby("feature").mean().sort_values(
                by="importance", ascending=False)[:50].index

            best_features = feature_importance.loc[feature_importance.feature.isin(cols)]

            plt.figure(figsize=(16, 12));
            sns.barplot(x="importance", y="feature", data=best_features.sort_values(by="importance", ascending=False));
            plt.title('LGB Features (avg over folds)');
        
            return oof, prediction, feature_importance
        return oof, prediction
    
    else:
        return oof, prediction

params = {'num_leaves': 128,
          'min_data_in_leaf': 79,
          'objective': 'huber',
          'max_depth': -1,
          'learning_rate': 0.01,
          "boosting": "gbdt",
          "bagging_freq": 5,
          "bagging_fraction": 0.8126672064208567,
          "bagging_seed": 11,
          "metric": 'mae',
          "verbosity": -1,
          'reg_alpha': 0.1302650970728192,
          'reg_lambda': 0.3603427518866501
         }


# In[ ]:


oof_lgb, prediction_lgb, feature_importance = train_model(params=params, model_type='lgb', plot_feature_importance=True)
top_cols = list(feature_importance[["feature", "importance"]].groupby("feature").mean().sort_values(
                by="importance", ascending=False)[:50].index)

plt.figure(figsize=(15, 6))
plt.plot(y_tr, color='g', label='y_train')
plt.plot(oof_lgb, color='b', label='lgb')
plt.legend(loc=(1, 0.5));
plt.title('lgb')


# Model is working well with certain range, but not with higher values.
# 
# ## Balance Dataset, Naive Oversampling

# In[ ]:


from imblearn.over_sampling import RandomOverSampler

def balance_train_data(X, y, random_state=42):
    ros = RandomOverSampler(random_state=random_state)
    X_index = np.array(range(len(X))).reshape(-1, 1)
    y_as_label = y_tr.time_to_failure.map(int)
    X_resampled_index, _ = ros.fit_sample(X_index, y_as_label)
    X_resampled_index = X_resampled_index.ravel()
    return X.iloc[X_resampled_index], y.iloc[X_resampled_index]

X_train_scaled2, y_tr2 = balance_train_data(X_train_scaled, y_tr)
visualize_class_balance('y_tr distribution oversampled', y_tr2.time_to_failure.map(int))
print(f'Now train data size is {len(y_tr2)}.')


# Perfect.
# 
# ### Train Naively Oversampled Dataset

# In[ ]:


oof_lgb2, prediction_lgb2, feature_importance2 = train_model(X=X_train_scaled2, X_test=X_test_scaled, y=y_tr2,
                                                             params=params, model_type='lgb',
                                                             plot_feature_importance=True)
plt.figure(figsize=(15, 6))
plt.plot(oof_lgb2, color='b', label='lgb')
plt.plot(y_tr2.reset_index(drop=True), color='g', label='y_train')
plt.legend(loc=(1, 0.5));
plt.title('lgb')


# Can you see the difference? Results around 12s to 16s are hidden...
# 
# __Because prediction results are overfitted to training samples, just being identical to the training signals.__
# 
# ## Balance Dataset again
# 
# Too much oversampling have caused overfitting. What if we do that modestly?

# In[ ]:


from collections import Counter
import random

def balance_class_by_limited_over_sampling(X, y, max_sample_per_class=None, multiply_limit=2., random_state=42):
    """Balance class distribution basically by oversampling but limited duplication.

    # Arguments
        X: Data samples, only size of samples is used here.
        y: Class labels to be balanced.
        max_sample_per_class: Number of maximum samples per class, large class will be limitd to this number.
        multiply_limit: Small size class samples will be duplicated, but limited to multiple of this number.
    """
    assert len(X) == len(y), f'Length of X({len(X)}) and y({len(y)}) are supposed to be the same.'
    y_count = Counter(y)
    max_sample_per_class = max_sample_per_class or np.max(list(y_count.values()))
    resampled_idxes = []
    random.seed(random_state)
    for cur_y, count in y_count.items():
        this_samples = np.min([multiply_limit * count, max_sample_per_class]).astype(int)
        idxes = np.where(y == cur_y)[0]
        idxes = random.choices(idxes, k=this_samples)
        resampled_idxes += list(idxes)
    return X[resampled_idxes], y[resampled_idxes]

def balance_train_data3(X, y, random_state=42):
    X_index = np.array(range(len(X)))
    y_as_label = y_tr.time_to_failure.map(int)
    X_resampled_index, _ = balance_class_by_limited_over_sampling(X_index, y_as_label, multiply_limit=2.)
    X_resampled_index = sorted(X_resampled_index)
    return X.iloc[X_resampled_index].reset_index(drop=True), y.iloc[X_resampled_index].reset_index(drop=True)

X_train_scaled3, y_tr3 = balance_train_data3(X_train_scaled, y_tr)
visualize_class_balance('y_tr distribution limited-over-resampled', y_tr3.time_to_failure.map(int))


# Well... Let's see.

# In[ ]:


oof_lgb3, prediction_lgb3, feature_importance3 = train_model(X=X_train_scaled3, X_test=X_test_scaled, y=y_tr3,
                                                             params=params, model_type='lgb',
                                                             plot_feature_importance=True)
plt.figure(figsize=(15, 6))
plt.plot(oof_lgb3, color='b', label='lgb')
plt.plot(y_tr3.reset_index(drop=True), color='g', label='y_train')
plt.legend(loc=(1, 0.5));
plt.title('lgb')


# Looks fine.
# 
# ## So, Results?
# 
# - __Trained as is: LB 1.540__
# - __Perfectly oversampled: LB 1.756__
# - __Modestly oversampled: LB 1.815__
# 
# I guess... we need augmentation. orz
# 
# To be continued... hopefully.

# In[ ]:



