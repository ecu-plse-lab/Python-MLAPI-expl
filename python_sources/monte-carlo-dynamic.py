#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import helpers
sns.set()
np.random.seed(42)


# ## Data Fetching

# In[ ]:


symbol = 'AAPL'
output_size = 'compact'


# In[ ]:


df_raw = helpers.fetch_data(symbol, output_size)
df = df_raw.copy()


# In[ ]:


df = df_raw.sort_values(by='timestamp')
df.head()


# ## Data Processing

# In[ ]:


simulation = pd.DataFrame()


# In[ ]:


number_simulation = 100
predict_days = 30


# In[ ]:


def percent_change (time_series, period=1):
    time_series = np.array(time_series)
    percent_change = (time_series[period:] - time_series[:-period]) / time_series[:-period]
    return percent_change


# ## Run Simulation

# In[ ]:


for i in tqdm(range(number_simulation)):
    price_list = df['adjusted_close'].values[-predict_days:].tolist()
    volatility = percent_change(price_list[-predict_days:]).std()
    for d in range(predict_days):
        price_list.append(price_list[-1] * (1 + np.random.normal(0, volatility)))
        volatility = percent_change(price_list[-predict_days:]).std()
    simulation[i] = pd.Series(price_list[-predict_days:]).values


# In[ ]:


simulation.head()


# In[ ]:


plt.style.use(['ggplot'])
plt.figure(figsize=(15,7))
plt.plot(simulation)
plt.title('Simulation', color='black')
plt.ylabel('Stock Price')
plt.xlabel('Simulation Days')
plt.show()


# In[ ]:


simulation_means = np.array([simulation[i].mean() for i in range(100)])


# In[ ]:


plt.style.use(['ggplot'])
plt.figure(figsize=(15,5))
plt.subplot(1,2,1)
sns.distplot(df['adjusted_close'],norm_hist=True)
plt.title('Simulation\nmean = {:.4f}\nstdev = {:.4f}\nskewness = {:.4f}\nkurtosis = {:.4f}'
      .format(np.mean(simulation_means), 
              np.std(simulation_means), 
              stats.skew(simulation_means), 
              stats.kurtosis(simulation_means)), color='black')
plt.xlabel('Close Price')

plt.subplot(1,2,2)
sns.distplot(simulation_means, norm_hist=True,label='Simulation')
sns.distplot(df['adjusted_close'],norm_hist=True,label='Sample')
plt.title('Sample\nmean = {:.4f}\nstdev = {:.4f}\nskewness = {:.4f}\nkurtosis = {:.4f}'
      .format(df['adjusted_close'].mean(), 
              df['adjusted_close'].std(), 
              df['adjusted_close'].skew(), 
              df['adjusted_close'].kurtosis()), color='black')
plt.xlabel('Close Price')

plt.legend()
plt.show()


# ## T Test for Mean

# In[ ]:


mean_real = df['adjusted_close'].mean()


# In[ ]:


t_statistic, p_value = helpers.t_test_1sample(alpha=0.05, 
                                              sample_array=simulation_means, 
                                              population_mean=mean_real)


# ## Confidence Interval for Mean

# In[ ]:


margin_error_real = helpers.moe_t_test_1sample(alpha=0.05, 
                                         sample_size=df['adjusted_close'].shape[0], 
                                         stdev=df['adjusted_close'].std())


# In[ ]:


lower_bound_real, upper_bound_real = helpers.confidence_interval(mean=df['adjusted_close'].mean(), 
                                                                 margin_of_error=margin_error_real)
print('Lower bound for real:', lower_bound_real)
print('Upper bound for real:', upper_bound_real)


# In[ ]:


margin_error_simulation = helpers.moe_t_test_1sample(0.05, 
                                               sample_size=simulation_means.shape[0], 
                                               stdev=simulation_means.std())


# In[ ]:


lower_bound_simulation, upper_bound_simulation = helpers.confidence_interval(
                                                    mean=simulation_means.mean(), 
                                                    margin_of_error=margin_error_simulation)
print('Lower bound for simulation:', lower_bound_simulation)
print('Upper bound for simulation:', upper_bound_simulation)


# ## Bartlett Test for Variance

# In[ ]:


b_statistic, p_value = helpers.bartlett(0.05, simulation_means, df['adjusted_close'])


# ## KS Test for Distribution

# In[ ]:


ks_statistic, p_value = helpers.ks_test_2sample(0.05, simulation_means, df['adjusted_close'])


# ----