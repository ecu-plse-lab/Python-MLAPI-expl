#!/usr/bin/env python
# coding: utf-8

# # Introduction
# **Coronaviruses are a large family of viruses which may cause illness in animals or humans. In humans, several coronaviruses are known to cause respiratory infections ranging from the common cold to more severe diseases such as Middle East Respiratory Syndrome (MERS) and Severe Acute Respiratory Syndrome (SARS). The most recently discovered coronavirus causes coronavirus disease COVID-19.COVID-19 is the infectious disease caused by the most recently discovered coronavirus. This new virus and disease were unknown before the outbreak began in Wuhan, China, in December 2019.**
# 
# * [Source](http://www.who.int/emergencies/diseases/novel-coronavirus-2019/question-and-answers-hub/q-a-detail/q-a-coronaviruses)
# <img src="https://i4.hurimg.com/i/hurriyet/75/0x0/5eb3121e67b0a908d8c64551.jpg" height = "422" width = "750" >
# 
# <hr> 
# 
# * If you are looking for a more general analysis you can check out my other kernel: [General Analysis of Covid-19](https://www.kaggle.com/mrhippo/general-analysis-of-covid-19)
# 
# ### Thanks to: 
# * [COVID-19 Case Study - Analysis, Viz & Comparisons](https://www.kaggle.com/tarunkr/covid-19-case-study-analysis-viz-comparisons) (Tarun Kumar)
# * [Analysis on Coronavirus](https://www.kaggle.com/vanshjatana/analysis-on-coronavirus) (Vansh Jatana)
# * [X-Ray Detection](https://www.kaggle.com/vanshjatana/x-ray-detection) (Vansh Jatana)
# <hr> 
# * This plot shows why we should take **protective measures** and how we can control this situation. 
# <img src="https://www.catalannews.com/images/cna/images/2020/03/flattening-the-curve.jpg" height = "422" width = "750" >
# 
# [Image Source](https://www.catalannews.com/society-science/item/how-the-health-department-s-new-app-to-monitor-coronavirus-symptoms-works)
# 
# 
# <hr>
# 
# 
# >## Content
# >1. [Imports](#0)
# >1. [Datasets and Preprocessing](#1)
# >1. [Maps](#2)
# >>    1. [World Map of Covid-19 ](#2.1)
# >>    1. [World Map of Confirmed Cases ](#2.2)
# >>    1. [World Map of Death Cases ](#2.3)
# >>    1. [World Map of Recovered Cases ](#2.4)
# >>    1. [World Map of Active Cases ](#2.5)
# >1. [Analysis](#3)
# >>    1. [Covid-19 in WHO Regions](#3.1)
# >>    1. [Covid-19 in Countries](#3.2)
# >1. [Comparisons](#4)
# >>    1. [WHO Regions](#4.1)
# >>    1. [Piecharts of WHO Regions](#4.2)
# >>    1. [Countries](#4.3)
# >>    1. [Piecharts of Countries](#4.4)
# >>    1. [Sorted Cases WHO Regions (Confirmed, Death, Recovered and Active)](#4.5)
# >>    1. [Table of WHO Regions](#4.6)
# >>    1. [Sorted State Percentages WHO Regions (Death, Recovered and Active Percentages)](#4.7)
# >>    1. [Top 10 Countries (Confirmed, Death, Recovered and Active)](#4.8)
# >>    1. [Table of Countries](#4.9)
# >>    1. [Top 10 Countries in Percentages (Death, Recovered and Active Percentage)](#4.91)
# >1. [Predictions](#6)
# >>    1. [Confirmed Prediction](#6.1)
# >>    1. [Death Prediction](#6.2)
# >>    1. [Recovered Prediction](#6.3)
# >>    1. [Prediction Table](#6.4)
# >1. [LSTM](#7)
# >1. [Last 10 Days](#8)
# >1. [Covid-19 in 3 Big Countries](#9)
# >>    1. [China](#9.1)
# >>        1. [Analysis](#9.11)
# >>        1. [Prediction](#9.12)
# >>            1. [Confirmed Prediction](#9.121)
# >>            1. [Death Prediction](#9.122)
# >>            1. [Prediction Table](#9.123)
# >>        1. [Last 5 Days](#9.13)
# >>    1. [United States](#9.2)
# >>        1. [Analysis](#9.21)
# >>        1. [Prediction](#9.22)
# >>            1. [Confirmed Prediction](#9.221)
# >>            1. [Death Prediction](#9.222)
# >>            1. [Prediction Table](#9.223)
# >>        1. [Last 5 Days](#9.23)
# >>    1. [United Kingdom](#9.3)
# >>        1. [Analysis](#9.31)
# >>        1. [Prediction](#9.32)
# >>            1. [Confirmed Prediction](#9.321)
# >>            1. [Death Prediction](#9.322)
# >>            1. [Prediction Table](#9.323)
# >>        1. [Last 5 Days](#9.33)
# >1. [Patient Data](#10)
# >1. [Covid-19 Classification From Lungs X-Rays](#11)
# >>    1. [CNN Model](#11.1)
# >>    1. [Training](#11.2)
# >>    1. [Result](#11.3)
# >>    1. [Confusion Matrix](#11.4)
# >1. [Conclusion](#12)

# <a id="0"></a> <br>
# # Imports
# * **Numpy:** Linear algebra - used sections: All
# * **Pandas:** Data manuplation and data science - used sections: All
# * **Matplotlib:** Simple visualization - used sections: All
# * **Seaborn:** Visualization - used sections: Analysis, Covid-19 Classification From Lung X-Rays
# * **Plotly:** Interactive plots - used sections: Except Predictions, LSTM, Covid-19 Classification From Lung X-Rays All
# * **Datetime:** Time data manuplation - used sections: Analysis, Predictions 
# * **Keras:** Deep learning - used sections: Predictions, LSTM, Covid-19 in 3 Big Countries, Covid-19 Classification From Lung X-Rays

# In[ ]:


# data science and visualization / used sections: Maps, Analysis, Comparisons, Top 10s, Patient Data
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import plotly.graph_objs as go 
from plotly.subplots import make_subplots
from plotly.offline import init_notebook_mode, iplot, plot
import plotly.express as px
import glob
init_notebook_mode(connected=True) 
import warnings
warnings.filterwarnings('ignore')
from datetime import date, timedelta, datetime

# deep learning (keras) / used sections: Predictions, Covid-19 in 3 Big Countries
from keras.layers import Input, Dense, Activation, LeakyReLU, Dropout
from keras import models
from keras.optimizers import RMSprop, Adam
# LSTM (keras) / used sections: LSTM
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM
from sklearn.metrics import mean_squared_error
from keras.layers import Dropout
import math
# CNN (keras and tensorflow) / used sections: Covid-19 Classification From Lung X-Rays
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator,load_img, img_to_array
from keras.models import Sequential, Model
from keras.layers import Conv2D, MaxPooling2D,GlobalAveragePooling2D
from keras.layers import Activation, Dropout, BatchNormalization, Flatten, Dense, AvgPool2D,MaxPool2D
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.optimizers import Adam, SGD, RMSprop
import tensorflow as tf 

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))


# <a id="1"></a> <br>
# # Datasets and Preprocessing

# In[ ]:


data = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/covid_19_data.csv")
data2 = pd.read_csv("/kaggle/input/corona-virus-report/covid_19_clean_complete.csv")
df_confirmed = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_confirmed.csv")
df_death = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_deaths.csv")
df_recovered = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_recovered.csv")


# In[ ]:


df_confirmed.head()


# In[ ]:


df_death.head()


# In[ ]:


df_recovered.head()


# In[ ]:


patient = pd.read_csv("/kaggle/input/patient/patient.csv")
patient = patient.drop(["group", "infection_order","infected_by","contact_number","confirmed_date","released_date","deceased_date"],axis = 1)
patient["age"] = 2020 - patient["birth_year"]

patient.head()


# In[ ]:


patient.describe()


# In[ ]:


patient.info()


# In[ ]:


data = data.drop(["Last Update"],axis = 1) #we will not use last update
data.head()


# In[ ]:


data["Active"] = data["Confirmed"] - data["Deaths"] - data["Recovered"]
data.tail()


# In[ ]:


data.describe()


# In[ ]:


from datetime import date, timedelta, datetime
data["ObservationDate"] = pd.to_datetime(data["ObservationDate"])
data.info()


# In[ ]:


data2["Date"] = pd.to_datetime(data2["Date"])
data2.info()


# <a id="2"></a> <br>
# # Maps

# <a id="2.1"></a> <br>
# ## World Map of Covid-19 

# In[ ]:


import plotly.express as px
grp = data.groupby(["ObservationDate","Country/Region"])["Confirmed","Deaths","Recovered"].max()
grp = grp.reset_index()
grp["ObservationDate"] = grp["ObservationDate"].dt.strftime("%m,%d,%Y")
grp["Active"] = grp["Confirmed"] - grp["Recovered"] - grp["Deaths"]
grp["Country"] = grp["Country/Region"]

fig = px.choropleth(grp, locations= "Country", locationmode = "country names",
                 color = "Confirmed", hover_name = "Country/Region",hover_data = [grp.Recovered, grp.Deaths, grp.Active],projection = "natural earth",
                 animation_frame = "ObservationDate",
                 color_continuous_scale = "Reds",
                 range_color = [10000,200000],
                 
                 title = "Covid-19 World Map")
fig.update(layout_coloraxis_showscale=True)
iplot(fig)


# * As you can see on the animation **Covid-19** starts spreading from **China** and spreads other countries by vehicles. 

# <a id="2.2"></a> <br>
# ## World Map of Confirmed Cases 

# In[ ]:


data_last = data.tail(1)
data_last_day = data[data["ObservationDate"] == data_last["ObservationDate"].iloc[0]] 
country_list = list(data_last_day["Country/Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["Country/Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_maps = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["Country/Region","Confirmed","Deaths","Recovered","Active"])


# In[ ]:


import plotly.express as px
grp = data_maps.groupby(["Country/Region"])["Confirmed"].max()
grp = grp.reset_index()
fig = px.choropleth(grp, locations = "Country/Region", 
                    color = np.log10(grp["Confirmed"]),
                    hover_name= grp["Country/Region"],
                    hover_data = ["Confirmed"],
                    color_continuous_scale=px.colors.sequential.Plasma,locationmode = "country names")
fig.update_geos(fitbounds = "locations",)
fig.update_layout(title_text = "Confirmed Cases on World Map(Log Scale)")
fig.update_coloraxes(colorbar_title = "Confirmed Cases (Log Scale)", colorscale = "Blues")
fig.show()


# <a id="2.3"></a> <br>
# ## World Map of Death Cases 

# In[ ]:


grp = data_maps.groupby(["Country/Region"])["Deaths"].max()
grp = grp.reset_index()
fig = px.choropleth(grp, locations = "Country/Region", 
                    color = np.log10(grp["Deaths"]),
                    hover_name= grp["Country/Region"],
                    hover_data = ["Deaths"],
                    color_continuous_scale=px.colors.sequential.Plasma,locationmode = "country names")
fig.update_geos(fitbounds = "locations",)
fig.update_layout(title_text = "Death Cases on World Map(Log Scale)")
fig.update_coloraxes(colorbar_title = "Death Cases (Log Scale)", colorscale = "Reds")
fig.show()


# <a id="2.4"></a> <br>
# ## World Map of Recovered Cases 

# In[ ]:


grp = data_maps.groupby(["Country/Region"])["Recovered"].max()
grp = grp.reset_index()
fig = px.choropleth(grp, locations = "Country/Region", 
                    color = np.log10(grp["Recovered"]),
                    hover_name= grp["Country/Region"],
                    hover_data = ["Recovered"],
                    color_continuous_scale=px.colors.sequential.Plasma,locationmode = "country names")
fig.update_geos(fitbounds = "locations",)
fig.update_layout(title_text = "Recovered Cases on World Map(Log Scale)")
fig.update_coloraxes(colorbar_title = "Recovered Cases (Log Scale)", colorscale = "Greens")
fig.show()


# <a id="2.5"></a> <br>
# ## World Map of Active Cases 

# In[ ]:


grp = data_maps.groupby(["Country/Region"])["Active"].max()
grp = grp.reset_index()
fig = px.choropleth(grp, locations = "Country/Region", 
                    color = np.log10(grp["Active"]),
                    hover_name= grp["Country/Region"],
                    hover_data = ["Active"],
                    color_continuous_scale=px.colors.sequential.Plasma,locationmode = "country names")
fig.update_geos(fitbounds = "locations",)
fig.update_layout(title_text = "Active Cases on World Map(Log Scale)")
fig.update_coloraxes(colorbar_title = "Active Cases (Log Scale)", colorscale = "Purples")
fig.show()


# <a id="3"></a> <br>
# # Analysis

# In[ ]:


date_list1 = list(data["ObservationDate"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in date_list1:
    x = data[data["ObservationDate"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
data_glob.head()


# In[ ]:


sns.pairplot(data_glob)
plt.show()
desc = data.describe()
print(desc[:3])


# In[ ]:


correlation = data_glob.corr() 

f,ax = plt.subplots(figsize=(12, 12))
sns.heatmap(correlation, annot=True,annot_kws = {"size": 12}, linewidths=0.5, fmt = '.3f', ax=ax, cmap = "BrBG", linecolor = "black")
plt.title("Correlations", fontsize = 20)
plt.show()


# In[ ]:


report_covid_global = data_glob.tail(1)
print("=======Global Covid-19 Report=======\nDate: {}\nTotal Confirmed: {}\nTotal Deaths: {}\nTotal Recovered: {}\nTotal Active: {}\n====================================".format(report_covid_global["Date"].iloc[0],int(report_covid_global["Confirmed"].iloc[0]),int(report_covid_global["Deaths"].iloc[0]),int(report_covid_global["Recovered"].iloc[0]),int(report_covid_global["Active"].iloc[0])))


# In[ ]:


trace1 = go.Scatter(
x = data_glob["Date"],
y = data_glob["Confirmed"],
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = data_glob["Date"],
y = data_glob["Deaths"],
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = data_glob["Date"],
y = data_glob["Recovered"],
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = data_glob["Date"],
y = data_glob["Active"],
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "Global Case States",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases",legend=dict(
        x=0,
        y=1,),hovermode='x unified')
    
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)


# * On this plot **confirmed cases** are increasing so fast but our **recovery** is increasing too. 

# In[ ]:


trace1 = go.Scatter(
x = data_glob["Date"],
y = np.log10(data_glob["Confirmed"]),
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = data_glob["Date"],
y = np.log10(data_glob["Deaths"]),
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = data_glob["Date"],
y = np.log10(data_glob["Recovered"]),
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = data_glob["Date"],
y = np.log10(data_glob["Active"]),
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "Global Case States (Log Scale)",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases (Log Scale)",legend=dict(
        x=0,
        y=1,),hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)


# In[ ]:


labels = ["Recovered","Deaths","Active"]
values = [data_glob.tail(1)["Recovered"].iloc[0],data_glob.tail(1)["Deaths"].iloc[0],data_glob.tail(1)["Active"].iloc[0]]

fig = go.Figure(data = [go.Pie(labels = labels, values = values,pull = [0.05,0.05,0.05],textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Global Patient Percentage"))
fig.show()


# In[ ]:


data_daily_confirmed = np.nan_to_num(df_confirmed.sum()[5:].diff())
data_daily_death = np.nan_to_num(df_death.sum()[5:].diff())
data_daily_recovered = np.nan_to_num(df_recovered.sum()[5:].diff())

dates = np.arange(0, len(data_daily_confirmed))

fig = go.Figure(data = [go.Scatter(x = dates,
                                  y = data_daily_confirmed,
                                  name = "Confirmed",
                                  mode = "lines",
                                  marker = dict(color = 'rgba(4,90,141, 0.8)')),
                       go.Scatter(x = dates,
                                  y = data_daily_death,
                                  name = "Deaths",
                                  mode = "lines",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)')),
                       go.Scatter(x = dates,
                                  y = data_daily_recovered,
                                  name = "Recovered",
                                  mode = "lines",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)'))], 
                layout = go.Layout(template = "plotly_white",
                                xaxis_title="Days",
                                yaxis_title="Number of Cases", 
                                title = "Daily Cases",
                                legend=dict(x=0,y=1,),
                                hovermode='x unified'))

iplot(fig)


# In[ ]:


fig = make_subplots(rows=3,cols=1,subplot_titles = ("Daily Confirmed","Daily Death","Daily Recovered"))

fig.append_trace(go.Box(
                  y = data_daily_confirmed,
                  name = "Daily Confirmed",
                  boxmean = "sd",
                  marker = dict(color = 'rgba(4,90,141, 0.8)')),row = 1, col = 1)

fig.append_trace(go.Box(
                  y = data_daily_death,
                  name = "Daily Death",
                  boxmean = "sd",
                  marker = dict(color = 'rgba(152,0,67, 0.8)')),row = 2, col = 1)
          
fig.append_trace(go.Box(
                  y = data_daily_recovered,
                  name = "Daily Recovered",
                  boxmean = "sd",
                  marker = dict(color = 'rgba(1,108,89, 0.8)')),row = 3, col = 1)
          
fig.update_layout(height = 1200, title = "Daily Cases Boxplots",template="plotly_white")

iplot(fig)


# In[ ]:


moving_average_short = []
moving_average_long = []

for i in range(1, len(data_daily_confirmed)):
    moving_average_short.append(data_daily_confirmed[i:i+10].mean())
    moving_average_long.append(data_daily_confirmed[i:i+25].mean())

dates2 = np.arange(1, len(data_daily_confirmed))
    
fig = go.Figure(data = [go.Bar(x = dates,
                              y = data_daily_confirmed,
                              name = "Daily Confirmed",
                              marker = dict(color = 'rgba(4,90,141, 0.8)')),
                       go.Scatter(x = dates2,
                              y = moving_average_short,
                                 mode = "lines",
                                 name = "Moving Average Short (10 days)",),
                       go.Scatter(x = dates2,
                              y = moving_average_long,
                                 mode = "lines",
                       name = "Moving Average Long (25 days)")],
               layout = go.Layout(template = "plotly_white",
                                xaxis_title="Days",
                                yaxis_title="Number of Cases", 
                                title = "Daily Confirmed Cases",
                                legend=dict(x=0,y=1,),
                                hovermode='x unified',
                                annotations=[
                                            dict(
                                                x=26,
                                                y=data_daily_confirmed[1:].mean() + 10000,
                                                xref="x",
                                                yref="y",
                                                text="Daily Confirmed Mean",
                                                showarrow=False,
                                                font = dict(size = 15,
                                                           color = "Black"))]))

fig.add_shape(
            type="line",
            x0=0,
            y0=data_daily_confirmed[1:].mean(),
            x1=len(dates)-0.7,
            y1=data_daily_confirmed[1:].mean(),
            line=dict(
                color="Orange",
                width=4,
                dash="dashdot",
            ),
    )

fig.show()


# In[ ]:


moving_average_short = []
moving_average_long = []

for i in range(1, len(data_daily_confirmed)):
    moving_average_short.append(data_daily_death[i:i+10].mean())
    moving_average_long.append(data_daily_death[i:i+25].mean())

dates2 = np.arange(1, len(data_daily_confirmed))
    
fig = go.Figure(data = [go.Bar(x = dates,
                              y = data_daily_death,
                              name = "Daily Death",
                              marker = dict(color = 'rgba(152,0,67, 0.8)')),
                       go.Scatter(x = dates2,
                              y = moving_average_short,
                                 mode = "lines",
                                 name = "Moving Average Short (10 days)",),
                       go.Scatter(x = dates2,
                              y = moving_average_long,
                                 mode = "lines",
                       name = "Moving Average Long (25 days)")],
               layout = go.Layout(template = "plotly_white",
                                xaxis_title="Days",
                                yaxis_title="Number of Cases", 
                                title = "Daily Death Cases",
                                legend=dict(x=0,y=1,),
                                hovermode='x unified',
                                annotations=[
                                            dict(
                                                x=22,
                                                y=data_daily_death[1:].mean() + 500,
                                                xref="x",
                                                yref="y",
                                                text="Daily Death Mean",
                                                showarrow=False,
                                                font = dict(size = 15,
                                                           color = "Black"))]))

fig.add_shape(
            type="line",
            x0=0,
            y0=data_daily_death[1:].mean(),
            x1=len(dates)-0.7,
            y1=data_daily_death[1:].mean(),
            line=dict(
                color="Black",
                width=4,
                dash="dashdot",
            ),
    )

fig.show()


# In[ ]:


moving_average_short = []
moving_average_long = []

for i in range(1, len(data_daily_confirmed)):
    moving_average_short.append(data_daily_recovered[i:i+10].mean())
    moving_average_long.append(data_daily_recovered[i:i+25].mean())

dates2 = np.arange(1, len(data_daily_confirmed))
    
fig = go.Figure(data = [go.Bar(x = dates,
                              y = data_daily_recovered,
                              name = "Daily Recovered",
                              marker = dict(color = 'rgba(1,108,89, 0.8)')),
                       go.Scatter(x = dates2,
                              y = moving_average_short,
                                 mode = "lines",
                                 name = "Moving Average Short (10 days)",),
                       go.Scatter(x = dates2,
                              y = moving_average_long,
                                 mode = "lines",
                       name = "Moving Average Long (25 days)")],
               layout = go.Layout(template = "plotly_white",
                                xaxis_title="Days",
                                yaxis_title="Number of Cases", 
                                title = "Daily Recovered Cases",
                                legend=dict(x=0,y=1,),
                                hovermode='x unified',
                                annotations=[
                                            dict(
                                                x=26,
                                                y=data_daily_recovered[1:].mean() + 16000,
                                                xref="x",
                                                yref="y",
                                                text="Daily Recovered Mean",
                                                showarrow=False,
                                                font = dict(size = 15,
                                                           color = "Black"))]))

fig.add_shape(
            type="line",
            x0=0,
            y0=data_daily_recovered[1:].mean(),
            x1=len(dates)-0.7,
            y1=data_daily_recovered[1:].mean(),
            line=dict(
                color="Orange",
                width=4,
                dash="dashdot",
            ),
    )

fig.show()


# In[ ]:


df_confirmed = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_confirmed.csv")
df_confirmed = df_confirmed.drop(["Lat", "Long"],axis=1)

case_num_country = df_confirmed.groupby("Country/Region").sum().apply(lambda x: x[x > 0].count(),axis = 0)    
d = [datetime.strptime(date, "%m/%d/%y").strftime("%d %b") for date in case_num_country.index]
list_num = []
list_num.append(case_num_country.tail(1).iloc[0])

plt.figure(figsize = (15,8))
plt.plot(d, case_num_country, marker = "o",markerfacecolor = "#ffffff",label = "Number of Infected Countries\nToday:"+str(list_num[0]))
plt.xticks(list(np.arange(0,len(d),int(len(d)/5))), d[:-1:int(len(d)/5)]+[d[-1]])

plt.xlabel("Date")
plt.ylabel("Number of Countries")
plt.title("Number of Infected Countries by Year")
plt.text(93,5,"Number of Inffected Countries (Today):" + str(list_num[0]),fontsize = 15)
plt.legend()
plt.grid(alpha = 0.4)

plt.show()


# In[ ]:


death_percent = ((data_glob["Deaths"]*100)/data_glob["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=data_glob["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Death Percentage(%)",title = "Death Percentage"))
iplot(fig)


# * **Death Percentage(Mortality Rate)** is a important data for epidemics. It can show how **dangerous** a epidemic is.  

# In[ ]:


recovered_percent = ((data_glob["Recovered"]*100)/data_glob["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=data_glob["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Recovered Percentage(%)",title = "Recovered Percentage"))
iplot(fig)


# * **Recovered Percentage(Recovery Rate)** can show how good health care system handle a epidemic.

# In[ ]:


active_percent = ((data_glob["Active"]*100)/data_glob["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=data_glob["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Active Percentage(%)",title = "Active Percentage"))
iplot(fig)


# * **Active Percentage** can show virus's impact time on people.

# <a id="3.1"></a> <br>
# ## Covid-19 in WHO Regions

# In[ ]:


country_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize = (14,24))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    
    ax = fig.add_subplot(len(country_list)/2,2,num)
    ax.plot(data_country["Date"],data_country["Confirmed"],label = "Confirmed\nToday:"+str(int(data_country.tail(1)["Confirmed"].iloc[0])),color = "darkcyan")
    ax.plot(data_country["Date"],data_country["Deaths"],color = "crimson",label = "Death\nToday:"+str(int(data_country.tail(1)["Deaths"].iloc[0])))
    ax.set_xlabel("Date")
    ax.set_ylabel("Values")
    plt.xticks(rotation = 25) #
    ax.legend(loc = "upper left")
    ax.fill_between(data_country["Date"],data_country["Confirmed"],color = "darkcyan",alpha = 0.3)
    ax.fill_between(data_country["Date"],data_country["Deaths"],color = "crimson",alpha = 0.3)
    ax.grid(True, alpha = 0.4)
    ax.set_title(n)
    text = "Death Percentage: "+str(np.round((100*data_country.tail(1)["Deaths"].iloc[0])/data_country.tail(1)["Confirmed"].iloc[0],2))+"\n"
    text += "Last 5 Days:\n"
    text += "Confirmed: "+str(data_country.tail(1)["Confirmed"].iloc[0])+"\n"
    text += "Deaths: "+str(data_country.tail(1)["Deaths"].iloc[0])
    plt.text(0.02,0.78,text,fontsize = 14, horizontalalignment="left",verticalalignment = "top",transform = ax.transAxes,bbox=dict(facecolor="white",alpha = 0.4))
    
plt.show()


# <a id="3.2"></a> <br>
# ## Covid-19 in Countries

# In[ ]:


country_list = ['Mainland China','US', 'Japan','South Korea','France',"Brazil",'Australia','Canada',
                "Germany","India","Italy",'UK','Russia','Spain','New Zealand','Turkey','Poland','Denmark']

fig = plt.figure(figsize = (14,69))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    
    ax = fig.add_subplot(len(country_list)/2,2,num)
    ax.plot(data_country["Date"],data_country["Confirmed"],label = "Confirmed\nToday:"+str(int(data_country.tail(1)["Confirmed"].iloc[0])),color = "darkcyan")
    ax.plot(data_country["Date"],data_country["Deaths"],color = "crimson",label = "Death\nToday:"+str(int(data_country.tail(1)["Deaths"].iloc[0])))
    ax.set_xlabel("Date")
    ax.set_ylabel("Values")
    plt.xticks(rotation = 25) #
    ax.legend(loc = "upper left")
    ax.fill_between(data_country["Date"],data_country["Confirmed"],color = "darkcyan",alpha = 0.3)
    ax.fill_between(data_country["Date"],data_country["Deaths"],color = "crimson",alpha = 0.3)
    ax.grid(True, alpha = 0.4)
    ax.set_title(n)
    text = "Death Percentage: "+str(np.round((100*data_country.tail(1)["Deaths"].iloc[0])/data_country.tail(1)["Confirmed"].iloc[0],2))+"\n"
    text += "Last 5 Days:\n"
    text += "Confirmed: "+str(data_country.tail(1)["Confirmed"].iloc[0])+"\n"
    text += "Deaths: "+str(data_country.tail(1)["Deaths"].iloc[0])
    plt.text(0.02,0.78,text,fontsize = 14, horizontalalignment="left",verticalalignment = "top",transform = ax.transAxes,bbox=dict(facecolor="white",alpha = 0.4))
    
plt.show()


# <a id="4"></a> <br>
# # Comparisons

# <a id="4.1"></a> <br>
# ## WHO Regions 

# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    plt.plot(data_country["Date"],data_country["Confirmed"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Confirmed"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Confirmed(M)")
plt.title("Confirmed Cases of WHO Regions")
plt.legend()
plt.show() 


# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    plt.plot(data_country["Date"],data_country["Deaths"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Deaths"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Deaths")
plt.title("Death Cases of WHO Regions")
plt.legend()
plt.show() 


# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    plt.plot(data_country["Date"],data_country["Recovered"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Recovered"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Recovered(M)")
plt.title("Recovered Cases of Countries")
plt.legend()
plt.show() 


# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    active = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
        active.append(sum(x["Active"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
    plt.plot(data_country["Date"],data_country["Active"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Active"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Active(M)")
plt.title("Active Cases of Countries")
plt.legend()
plt.show() 


# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    death_percent = ((data_country["Deaths"]*100)/data_country["Confirmed"])
    plt.plot(data_country["Date"],death_percent,"-o",linewidth = 2,markevery = [-1],label = n+": "+str(np.round(death_percent[len(death_percent)-1],2)))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Death Percentage(%)")
plt.title("Death Percentages of Countries")
plt.legend()
plt.show()


# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    recovered_percent = ((data_country["Recovered"]*100)/data_country["Confirmed"])
    plt.plot(data_country["Date"],recovered_percent,"-o",linewidth = 2,markevery = [-1],label = n+": "+str(np.round(recovered_percent[len(recovered_percent)-1],2)))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Recovered Percentage(%)")
plt.title("Recovered Percentages of Countries")
plt.legend()
plt.show()


# In[ ]:


region_list = list(data2["WHO Region"].unique())

fig = plt.figure(figsize=(15,10))
for n, num in zip(region_list, range(1,len(region_list)+1)):
    data_country = data2[data2["WHO Region"] == n]
    date_list1 = list(data_country["Date"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["Date"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
    active_percent = ((data_country["Active"]*100)/data_country["Confirmed"])
    plt.plot(data_country["Date"],active_percent,"-o",linewidth = 2,markevery = [-1],label = n+": "+str(np.round(active_percent[len(active_percent)-1],2)))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Active Percentage(%)")
plt.title("Active Percentages of Countries")
plt.legend()
plt.show()


# <a id="4.2"></a> <br>
# ## Piecharts of WHO Regions

# In[ ]:


data_last = data2.tail(1)
data_last_day = data2[data2["Date"] == data_last["Date"].iloc[0]] 
country_list = list(data_last_day["WHO Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["WHO Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob_who = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["Country","Confirmed","Deaths","Recovered","Active"])
data_glob_who.head()


# In[ ]:


country_list = list(data2["WHO Region"].unique())

country_list_15 = data_glob_who[data_glob_who["Country"].isin(country_list)]

labels = list(country_list_15["Country"])   
values = list(country_list_15["Confirmed"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole=.5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "WHO Regions' Confirmed Percentage Total: "+str(int(data_glob["Confirmed"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                    annotations=[dict(text="Confirmed Percentage", x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# In[ ]:


country_list = list(data2["WHO Region"].unique())

country_list_15 = data_glob_who[data_glob_who["Country"].isin(country_list)]

labels = list(country_list_15["Country"])   
values = list(country_list_15["Deaths"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole=.5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "WHO Regions' Death Percentage Total: "+str(int(data_glob["Deaths"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                    annotations=[dict(text="Death Percentage", x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# In[ ]:


country_list = list(data2["WHO Region"].unique())

country_list_15 = data_glob_who[data_glob_who["Country"].isin(country_list)]

labels = list(country_list_15["Country"])   
values = list(country_list_15["Recovered"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole=.5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "WHO Regions' Recovered Percentage Total: "+str(int(data_glob["Recovered"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                    annotations=[dict(text="Recovered Percentage", x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# In[ ]:


country_list = list(data2["WHO Region"].unique())

country_list_15 = data_glob_who[data_glob_who["Country"].isin(country_list)]

labels = list(country_list_15["Country"])   
values = list(country_list_15["Active"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole=.5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "WHO Regions' Active Percentage Total: "+str(int(data_glob["Active"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                    annotations=[dict(text="Active Percentage", x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# <a id="4.3"></a> <br>
# ## Countries

# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    plt.plot(data_country["Date"],data_country["Confirmed"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Confirmed"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Confirmed(M)")
plt.title("Confirmed Cases of Countries")
plt.legend()
plt.show() 


# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    plt.plot(data_country["Date"],data_country["Deaths"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Deaths"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Deaths")
plt.title("Death Cases of Countries")
plt.legend()
plt.show() 


# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    plt.plot(data_country["Date"],data_country["Recovered"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Recovered"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Recovered(M)")
plt.title("Recovered Cases of Countries")
plt.legend()
plt.show() 


# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    active = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
        active.append(sum(x["Active"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
    plt.plot(data_country["Date"],data_country["Active"],"-o",linewidth = 2,markevery = [-1],label = n+": "+str(data_country.tail(1)["Active"].iloc[0]))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Active(M)")
plt.title("Active Cases of Countries")
plt.legend()
plt.show() 


# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    death_percent = ((data_country["Deaths"]*100)/data_country["Confirmed"])
    plt.plot(data_country["Date"],death_percent,"-o",linewidth = 2,markevery = [-1],label = n+": "+str(np.round(death_percent[len(death_percent)-1],2)))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Death Percentage(%)")
plt.title("Death Percentages of Countries")
plt.legend()
plt.show() 


# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered)),columns = ["Date","Confirmed","Deaths","Recovered"])
    recovered_percent = ((data_country["Recovered"]*100)/data_country["Confirmed"])
    plt.plot(data_country["Date"],recovered_percent,"-o",linewidth = 2,markevery = [-1],label = n+": "+str(np.round(recovered_percent[len(recovered_percent)-1],2)))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Recovered Percentage(%)")
plt.title("Recovered Percentages of Countries")
plt.legend()
plt.show() 


# In[ ]:


country_list = ['Mainland China','US','South Korea','France',
                "Germany","India","Italy",'UK','Spain','Turkey']

fig = plt.figure(figsize=(15,10))
for n, num in zip(country_list, range(1,len(country_list)+1)):
    data_country = data[data["Country/Region"] == n]
    date_list1 = list(data_country["ObservationDate"].unique())
    confirmed = []
    deaths = []
    recovered = []
    active = []
    for i in date_list1:
        x = data_country[data_country["ObservationDate"] == i]
        confirmed.append(sum(x["Confirmed"]))
        deaths.append(sum(x["Deaths"]))
        recovered.append(sum(x["Recovered"]))
        active.append(sum(x["Active"]))
    data_country = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
    active_percent = ((data_country["Active"]*100)/data_country["Confirmed"])
    plt.plot(data_country["Date"],active_percent,"-o",linewidth = 2,markevery = [-1],label = n+": "+str(np.round(active_percent[len(active_percent)-1],2)))

plt.grid(True, alpha = .3)
plt.xlabel("Date")
plt.ylabel("Active Percentage(%)")
plt.title("Active Percentages of Countries")
plt.legend()
plt.show() 


# <a id="4.4"></a> <br>
# ## Piecharts of Countries

# In[ ]:


data_last = data.tail(1)
data_last_day = data[data["ObservationDate"] == data_last["ObservationDate"].iloc[0]] 
country_list = list(data_last_day["Country/Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["Country/Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob_country = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["Country","Confirmed","Deaths","Recovered","Active"])
data_glob_country.head()


# In[ ]:


country_list = ['Mainland China','US', 'Japan','South Korea','France','Australia','Canada',
                "Germany","India","Italy",'UK','Russia','Spain','New Zealand','Turkey',"Others"] #16

country_list_15 = data_glob_country[data_glob_country["Country"].isin(country_list)]
country_list_others = data_glob_country[data_glob_country["Country"].isin(country_list) == False]

country_list_others_new = country_list_others.drop(["Country"], axis = 1)
country_list_others_new = country_list_others_new.sum()
new_row = {"Country":"Others","Confirmed":country_list_others_new.iloc[0],"Deaths":country_list_others_new.iloc[1],"Recovered":country_list_others_new.iloc[2],"Active":country_list_others_new.iloc[3]}
country_list_15 = country_list_15.append(new_row,ignore_index=True)

labels = list(country_list_15["Country"])   
values = list(country_list_15["Confirmed"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole=.5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Countries' Confirmed Percentage Total: "+str(int(data_glob["Confirmed"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                    annotations=[dict(text="Confirmed Percentage", x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# In[ ]:


labels = list(country_list_15["Country"])   
values = list(country_list_15["Deaths"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole = .5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Countries' Death Percentage Total: "+str(int(data_glob["Deaths"].iloc[-1])),width = 800, height = 800,
                                                                                                                                            annotations=[dict(text='Death Percentage', x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# In[ ]:


labels = list(country_list_15["Country"])   
values = list(country_list_15["Recovered"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole = .5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Countries' Recovered Percentage Total: "+str(int(data_glob["Recovered"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                      annotations=[dict(text='Recovered Percentage', x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# In[ ]:


labels = list(country_list_15["Country"])   
values = list(country_list_15["Active"])

fig = go.Figure(data = [go.Pie(labels = labels, values = values,hole = .5,textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Countries' Active Percentage Total: "+str(int(data_glob["Active"].iloc[-1])),width = 800, height = 800,
                                                                                                                                                      annotations=[dict(text='Active Percentage', x=0.5, y=0.5, font_size=20, showarrow=False)]))
fig.show()


# <a id="4.5"></a> <br>
# ## Sorted Cases WHO Regions (Confirmed, Death, Recovered and Active)

# In[ ]:


data_last = data2.tail(1)
data_last_day = data2[data2["Date"] == data_last["Date"].iloc[0]] 
country_list = list(data_last_day["WHO Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["WHO Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob_who = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["WHO Region","Confirmed","Deaths","Recovered","Active"])
data_glob_who.head(10)


# In[ ]:


confirmed_sorted = data_glob_who.sort_values(by = ["Confirmed"])
confirmed_sorted.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = confirmed_sorted["WHO Region"],
                              y = confirmed_sorted["Confirmed"],
                              text = confirmed_sorted["Confirmed"],
                              textposition = "outside",
                              marker=dict(color = confirmed_sorted["Confirmed"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Confirmed"),colorscale="tempo",))],
                              layout = go.Layout(template= "plotly_white",title = "Confirmed Cases Sorted WHO Regions",xaxis_title="WHO Region",yaxis_title="Confirmed"))
iplot(fig)


# In[ ]:


confirmed_sorted = data_glob_who.sort_values(by = ["Deaths"])
confirmed_sorted.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = confirmed_sorted["WHO Region"],
                              y = confirmed_sorted["Deaths"],
                              text = confirmed_sorted["Deaths"],
                              textposition = "outside",
                              marker=dict(color = confirmed_sorted["Deaths"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Deaths"),colorscale="amp",))],
                              layout = go.Layout(template= "plotly_white",title = "Death Cases Sorted WHO Regions",xaxis_title="WHO Region",yaxis_title="Death"))
iplot(fig)


# In[ ]:


confirmed_sorted = data_glob_who.sort_values(by = ["Recovered"])
confirmed_sorted.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = confirmed_sorted["WHO Region"],
                              y = confirmed_sorted["Recovered"],
                              text = confirmed_sorted["Recovered"],
                              textposition = "outside",
                              marker=dict(color = confirmed_sorted["Recovered"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Recovered"),colorscale="speed",))],
                              layout = go.Layout(template= "plotly_white",title = "Recovered Cases Sorted WHO Regions",xaxis_title="WHO Region",yaxis_title="Recovered"))
iplot(fig)


# In[ ]:


confirmed_sorted = data_glob_who.sort_values(by = ["Active"])
confirmed_sorted.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = confirmed_sorted["WHO Region"],
                              y = confirmed_sorted["Active"],
                              text = confirmed_sorted["Active"],
                              textposition = "outside",
                              marker=dict(color = confirmed_sorted["Active"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Active"),colorscale="matter",))],
                              layout = go.Layout(template= "plotly_white",title = "Active Cases Sroted WHO Regions",xaxis_title="WHO Region",yaxis_title="Active"))
iplot(fig)


# <a id="4.6"></a> <br>
# ## Table of WHO Countries

# In[ ]:


data_glob_who.index = data_glob_who["WHO Region"]
data_glob_who = data_glob_who.drop(["WHO Region"],axis = 1)
data_glob_who["Death_percentage"] = np.round(100*data_glob_who["Deaths"]/data_glob_who["Confirmed"],2)
data_glob_who["Recover_percentage"] = np.round(100*data_glob_who["Recovered"]/data_glob_who["Confirmed"],2)
data_glob_who["Active_percentage"] = np.round(100*data_glob_who["Active"]/data_glob_who["Confirmed"],2)


# In[ ]:


data_glob_who.sort_values("Confirmed", ascending = False).style.background_gradient(cmap="Blues",subset =["Confirmed"]).background_gradient(cmap="Reds", subset = ["Deaths"]).background_gradient(cmap="Greens", subset = ["Recovered"]).background_gradient(cmap="Purples", subset = ["Active"]).background_gradient(cmap="OrRd", subset = ["Death_percentage"]).background_gradient(cmap="BuGn", subset = ["Recover_percentage"]).background_gradient(cmap="BuPu", subset = ["Active_percentage"]).format("{:.0f}",subset = ["Confirmed","Deaths","Recovered","Active"]).format("{:.2f}",subset = ["Death_percentage","Recover_percentage","Active_percentage"])


# <a id="4.7"></a> <br>
# ## Sorted State Percentages WHO Regions (Death, Recovered and Active Percentages)

# In[ ]:


data_last = data2.tail(1)
data_last_day = data2[data2["Date"] == data_last["Date"].iloc[0]] 
country_list = list(data_last_day["WHO Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["WHO Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob_who = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["WHO Region","Confirmed","Deaths","Recovered","Active"])
data_glob_who.head(10)


# In[ ]:


conf_death = data_glob_who["Deaths"]*100/data_glob_who["Confirmed"]
conf_death_df = pd.DataFrame(list(zip(data_glob_who["WHO Region"],conf_death)),columns = ["WHO Region","Deaths_percentage"])
conf_death_sorted = conf_death_df.sort_values(by = ["Deaths_percentage"])
conf_death_10 = conf_death_sorted.tail(10)
conf_death_10.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = conf_death_10["WHO Region"],
                              y = conf_death_10["Deaths_percentage"],
                              text = np.round(conf_death_10["Deaths_percentage"],2),
                              textposition = "outside",
                              marker=dict(color = conf_death_10["Deaths_percentage"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Death Percentage(%)"),colorscale="PuRd",))],
                              layout = go.Layout(template= "plotly_white",title = "Death Percentage Sorted WHO Regions",xaxis_title="WHO Region",yaxis_title="Death Percentage(%)"))
iplot(fig)


# In[ ]:


conf_recovered = data_glob_who["Recovered"]*100/data_glob_who["Confirmed"]
conf_recovered_df = pd.DataFrame(list(zip(data_glob_who["WHO Region"],conf_recovered)),columns = ["WHO Region","Recovered_percentage"])
conf_recovered_sorted = conf_recovered_df.sort_values(by = ["Recovered_percentage"])
conf_recovered_10 = conf_recovered_sorted.tail(10)
conf_recovered_10.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = conf_recovered_10["WHO Region"],
                              y = conf_recovered_10["Recovered_percentage"],
                              text = np.round(conf_recovered_10["Recovered_percentage"],2),
                              textposition = "outside",
                              marker=dict(color = conf_recovered_10["Recovered_percentage"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Recovered Percentage(%)"),colorscale="PuBuGn",))],
                              layout = go.Layout(template= "plotly_white",title = "Recovered Percentage Sorted WHO Regions",xaxis_title="WHO Region",yaxis_title="Recovered Percentage(%)"))
iplot(fig)


# In[ ]:


conf_active = data_glob_who["Active"]*100/data_glob_who["Confirmed"]
conf_active_df = pd.DataFrame(list(zip(data_glob_who["WHO Region"],conf_active)),columns = ["WHO Region","Active_percentage"])
conf_active_sorted = conf_active_df.sort_values(by = ["Active_percentage"])
conf_active_10 = conf_active_sorted.tail(10)
conf_active_10.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = conf_active_10["WHO Region"],
                              y = conf_active_10["Active_percentage"],
                              text = np.round(conf_active_10["Active_percentage"],2),
                              textposition = "outside",
                              marker=dict(color = conf_active_10["Active_percentage"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Active Percentage(%)"),colorscale="RdPu",))],
                              layout = go.Layout(template= "plotly_white",title = "Active Percentage Sorted WHO Regions",xaxis_title="WHO Region",yaxis_title="Active Percentage(%)"))
iplot(fig)


# <a id="4.8"></a> <br>
# ## Top 10 Countries (Confirmed, Death, Recovered and Active)

# In[ ]:


data_last = data.tail(1)
data_last_day = data[data["ObservationDate"] == data_last["ObservationDate"].iloc[0]] 
country_list = list(data_last_day["Country/Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["Country/Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob_country = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["Country","Confirmed","Deaths","Recovered","Active"])
data_glob_country.head()


# In[ ]:


confirmed_sorted = data_glob_country.sort_values(by = ["Confirmed"])
confirmed_sorted.tail(10)


# In[ ]:


confirmed_10 = confirmed_sorted.tail(10)

fig = go.Figure(data = [go.Bar(x = confirmed_10["Country"],
                              y = confirmed_10["Confirmed"],
                              text = confirmed_10["Confirmed"],
                              textposition = "outside",
                              marker=dict(color = confirmed_10["Confirmed"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Confirmed"),colorscale="tempo",))],
                              layout = go.Layout(template= "plotly_white",title = "Confirmed Cases Top 10 Countries",xaxis_title="Country",yaxis_title="Confirmed"))
iplot(fig)


# In[ ]:


confirmed_sorted = data_glob_country.sort_values(by = ["Deaths"])
confirmed_sorted.tail(10)


# In[ ]:


confirmed_10 = confirmed_sorted.tail(10)

fig = go.Figure(data = [go.Bar(x = confirmed_10["Country"],
                              y = confirmed_10["Deaths"],
                              text = confirmed_10["Deaths"],
                              textposition = "outside",
                              marker=dict(color = confirmed_10["Deaths"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Deaths"),colorscale="amp",))],
                              layout = go.Layout(template= "plotly_white",title = "Death Cases Top 10 Countries",xaxis_title="Country",yaxis_title="Death"))
iplot(fig)


# In[ ]:


confirmed_sorted = data_glob_country.sort_values(by = ["Recovered"])
confirmed_sorted.tail(10)


# In[ ]:


confirmed_10 = confirmed_sorted.tail(10)

fig = go.Figure(data = [go.Bar(x = confirmed_10["Country"],
                              y = confirmed_10["Recovered"],
                              text = confirmed_10["Recovered"],
                              textposition = "outside",
                              marker=dict(color = confirmed_10["Recovered"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Recovered"),colorscale="speed",))],
                              layout = go.Layout(template= "plotly_white",title = "Recovered Cases Top 10 Countries",xaxis_title="Country",yaxis_title="Recovered"))
iplot(fig)


# In[ ]:


confirmed_sorted = data_glob_country.sort_values(by = ["Active"])
confirmed_sorted.tail(10)


# In[ ]:


confirmed_10 = confirmed_sorted.tail(10)

fig = go.Figure(data = [go.Bar(x = confirmed_10["Country"],
                              y = confirmed_10["Active"],
                              text = confirmed_10["Active"],
                              textposition = "outside",
                              marker=dict(color = confirmed_10["Active"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Active"),colorscale="matter",))],
                              layout = go.Layout(template= "plotly_white",title = "Active Cases Top 10 Countries",xaxis_title="Country",yaxis_title="Active"))
iplot(fig)


# <a id="4.9"></a> <br>
# ## Table of Countries

# In[ ]:


data_glob_country.index = data_glob_country["Country"]
data_glob_country = data_glob_country.drop(["Country"],axis = 1)
data_glob_country["Death_percentage"] = np.round(100*data_glob_country["Deaths"]/data_glob_country["Confirmed"],2)
data_glob_country["Recover_percentage"] = np.round(100*data_glob_country["Recovered"]/data_glob_country["Confirmed"],2)
data_glob_country["Active_percentage"] = np.round(100*data_glob_country["Active"]/data_glob_country["Confirmed"],2)


# In[ ]:


data_glob_country.sort_values("Confirmed", ascending = False).style.background_gradient(cmap="Blues",subset =["Confirmed"]).background_gradient(cmap="Reds", subset = ["Deaths"]).background_gradient(cmap="Greens", subset = ["Recovered"]).background_gradient(cmap="Purples", subset = ["Active"]).background_gradient(cmap="OrRd", subset = ["Death_percentage"]).background_gradient(cmap="BuGn", subset = ["Recover_percentage"]).background_gradient(cmap="BuPu", subset = ["Active_percentage"]).format("{:.0f}",subset = ["Confirmed","Deaths","Recovered","Active"]).format("{:.2f}",subset = ["Death_percentage","Recover_percentage","Active_percentage"])


# <a id="4.91"></a> <br>
# ## Top 10 Countries in Percentages (Death, Recovered and Active Percentage)   

# In[ ]:


data_last = data.tail(1)
data_last_day = data[data["ObservationDate"] == data_last["ObservationDate"].iloc[0]] 
country_list = list(data_last_day["Country/Region"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in country_list:
    x = data_last_day[data_last_day["Country/Region"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
data_glob_country = pd.DataFrame(list(zip(country_list,confirmed,deaths,recovered,active)),columns = ["Country","Confirmed","Deaths","Recovered","Active"])


# In[ ]:


conf_death = data_glob_country["Deaths"]*100/data_glob_country["Confirmed"]
conf_death_df = pd.DataFrame(list(zip(data_glob_country["Country"],conf_death)),columns = ["Country","Deaths_percentage"])
conf_death_sorted = conf_death_df.sort_values(by = ["Deaths_percentage"])
conf_death_10 = conf_death_sorted.tail(10)
conf_death_10.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = conf_death_10["Country"],
                              y = conf_death_10["Deaths_percentage"],
                              text = np.round(conf_death_10["Deaths_percentage"],2),
                              textposition = "outside",
                              marker=dict(color = conf_death_10["Deaths_percentage"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Death Percentage(%)"),colorscale="PuRd",))],
                              layout = go.Layout(template= "plotly_white",title = "Death Percentage Top 10 Countries",xaxis_title="Country",yaxis_title="Death Percentage(%)"))
iplot(fig)


# In[ ]:


conf_recovered = data_glob_country["Recovered"]*100/data_glob_country["Confirmed"]
conf_recovered_df = pd.DataFrame(list(zip(data_glob_country["Country"],conf_recovered)),columns = ["Country","Recovered_percentage"])
conf_recovered_sorted = conf_recovered_df.sort_values(by = ["Recovered_percentage"])
conf_recovered_10 = conf_recovered_sorted.tail(10)
conf_recovered_10.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = conf_recovered_10["Country"],
                              y = conf_recovered_10["Recovered_percentage"],
                              text = np.round(conf_recovered_10["Recovered_percentage"],2),
                              textposition = "outside",
                              marker=dict(color = conf_recovered_10["Recovered_percentage"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Recovered Percentage(%)"),colorscale="PuBuGn",))],
                              layout = go.Layout(template= "plotly_white",title = "Recovered Percentage Top 10 Countries",xaxis_title="Country",yaxis_title="Recovered Percentage(%)"))
iplot(fig)


# In[ ]:


conf_active = data_glob_country["Active"]*100/data_glob_country["Confirmed"]
conf_active_df = pd.DataFrame(list(zip(data_glob_country["Country"],conf_active)),columns = ["Country","Active_percentage"])
conf_active_sorted = conf_active_df.sort_values(by = ["Active_percentage"])
conf_active_10 = conf_active_sorted.tail(10)
conf_active_10.head(10)


# In[ ]:


fig = go.Figure(data = [go.Bar(x = conf_active_10["Country"],
                              y = conf_active_10["Active_percentage"],
                              text = np.round(conf_active_10["Active_percentage"],2),
                              textposition = "outside",
                              marker=dict(color = conf_active_10["Active_percentage"],line = dict(color = "rgb(0,0,0)", width = 1.5),colorbar=dict(title="Active Percentage(%)"),colorscale="RdPu",))],
                              layout = go.Layout(template= "plotly_white",title = "Active Percentage Top 10 Countries",xaxis_title="Country",yaxis_title="Active Percentage(%)"))
iplot(fig)


# <a id="6"></a> <br>
# # Predictions
# * For predicting the feature of epidemic we will use **Deep Learning**. In this model we will give the **days** and **log scaled datas** to an **ANN Model**. We are **log scaling the data to normalize** it. 
# <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA8kAAAIcCAYAAADFSOyxAAAgAElEQVR4XuydB5hVxd3/f9tZll6lSN2lGBSkC6JIF6OxxBo1RTFqYoItxUf/yfvq+8ZEscSOijWJJpr4agRpIihgjYqKsixVeq/LsvX/fGc5u3fvnnvvnDPn3nvOvd/jw4Pszsz5zWfmzG++UzNqampqhA8JkAAJkAAJkAAJkAAJkAAJkAAJkIBkUCSzFpAACZAACZAACZAACZAACZAACZBALQGKZNYEEiABEiABEiABEiABEiABEiABEjhGgCKZVYEESIAESIAESIAESIAESIAESIAEKJJZB0iABEiABEiABEiABEiABEiABEigIQHOJLNGkAAJkAAJkAAJkAAJkAAJkAAJkABnklkHSIAESIAESIAESIAESIAESIAESIAzyawDJEACJEACJEACJEACJEACJEACJGBLgMutWTFIgARIgARIgARIgARIgARIgARI4BgBimRWBRIgARIgARIgARIgARIgARIgARKgSGYdIAESIAESIAESIAESIAESIAESIIGGBDiTzBpBAiRAAiRAAiRAAiRAAiRAAiRAApxJZh0gARIgARIgARIgARIgARIgARIgAc4ksw6QAAmQAAmQAAmQAAmQAAmQAAmQgC0BLrdmxSABEiABEiABEiABEiABEiABEiCBYwQoklkVSIAESIAESIAESIAESIAESIAESIAimXWABEiABEiABEiABEiABEiABEiABBoS4EwyawQJkAAJkAAJkAAJkAAJkAAJkAAJcCaZdYAESIAESIAESIAESIAESIAESIAEOJPMOkACJEACJEACJEACJEACJEACJEACtgS43JoVgwRIgARIgARIgARIgARIgARIgASOEaBIZlUgARIgARIgARIgARIgARIgARIgAYpk1gESIAESIAESIAESIAESIAESIAESaEiAM8msESRAAiRAAiRAAiRAAiRAAiRAAiTAmWTWARIgARIgARIgARIgARIgARIgARLgTDLrAAmQAAmQAAmQAAmQAAmQAAmQAAnYEuBya1YMEiABEiABEiCBwBAoLi6WTZs2KXvbtm0rAwcOjLvt+/fvl6+//lpKS0sT+t64Z4wvIAESIAESoEhmHSABEiABEiABEggugY0bN0r37t0bZGDhwoUybty4uGbq7bfflvHjxzd4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AV8QsBNpkURoly5d1BLlPn36xLQdYur++++3XcoLgf3b3/5W7fkN3ZMa6d7bSEuCYYS1FHvcuHExbYp2fZQVGXusreuYdPIZ/lLsye3YsWODH4ffdRz6S7uBgGjhnaaPd0E4RmOIMFgVAIYdOnSIyRE2/O53v7MtWwxWYLYZ6YTnLZYA96J8wt+Jsnzqqae08hUz4wxAAiRAAiTgOwIUyb4rEhpEAiRAAiQQiwAE1datW9WsYtu2baVTp06uBAvSwRLkTZs2qVd27dpVWrVq5SotLBvGn5KSkjrzsQ8b+5N1RGKsPPv192BYVlZWl2+UR+vWrV0dUIY8hpdtjx496vadmzBI1/IxYca4JEACJJCuBCiS07XkmW8SIAESIAESIAESIAESIAESIIFGBCiSWSlIgARIgARIgARIgARIgARIgARI4BgBimRWBRIgARIgARIgARIgARIgARIgARKgSGYdIAESIAESIAESIAESIAESIAESIIGGBDiTzBpBAiRAAiRAAiRAAiRAAiRAAiRAApxJZh0gARIgARIgARIgARIgARIgARIgAc4ksw6QAAmQAAmQAAmQAAmQAAmQAAmQgC0BLrdmxSABEiABEiABEiABEiABEiABEiCBYwQoklkVSIAESIAESIAESIAESIAESIAESIAimXWABEiABEiABEiABEiABEiABEiABBoS4EwyawQJkAAJkAAJkAAJkAAJkAAJkAAJcCaZdYAESIAESIAESIAESIAESIAESIAEOJPMOkACJEACJEACJEACJEACJEACJEACtgS43JoVgwRIgARIgARIgARIgARIgARIgASOEaBIZlUgARIgARIgARIgARIgARIgARIgAYpk1gESIAESIAESIAESIAESIAESIAESaEiAM8msESRAAiRAAiRAAiRAAiRAAiRAAiTAmWTWARIgARIgARIgARIgARIgARIgARLgTDLrAAmQAAmQAAmQAAmQAAmQAAmQAAnYEuBya1YMEiABEiABEiABEiABEiABEiABEjhGgCKZVYEESIAESIAESIAESIAESIAESIAEKJJZB0iABEiABEiABEiABEiABEiABEigIQHOJLNGkAAJkAAJkAAJkAAJkAAJkAAJkABnklkHSIAESIAESIAESIAESIAESIAESIAzyawDJEACJEACJEACJEACJEACJEACJGBLgMut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yGN/X5LqZRY1f+eNGyS/+tFEXzFgufiqOGiMQwL8phwCY3ASiEGA3xSrCAl4S4DflLc8mRoJePFN+Uoks0hJgARIgARIgARIgARIgARIgARIIJkEKJKTSZ/vJgESIAESIAESIAESIAESIAES8BUBimRfFQeNIQESIAESIAESIAESIAESIAESSCYBiuRk0ue7SYAESIAESIAESIAESIAESIAEfEWAItlXxUFjSIAESIAESIAESIAESIAESIAEkkmAIjmZ9PluEiABEiABEiABEiABEiABEiABXxGgSPZVcdAYEiABEiABEiABEiABEiABEiCBZBKgSE4mfb6bBEiABEiABEiABEiABEiABEjAVwQokn1VHDSGBEiABEiABEiABEiABEiABEggmQQokpNJn+8mARIgARIgARIgARIgARIgARLwFQGKZF8VB40hARIgARIgARIgARIgARIgARJIJgGK5GTS57tJgARIgARIgARIgARIgARIgAR8RYAi2VfFQWNIgARIgARIgARIgARIgARIgASSSYAiOZn0+W4SIIH/396bgNtRVXnf686ZJ0JCGAKEDMxTACEBhJAIiQTklVZQAWntC9r2S2hxeFr8+nk/+LpVBhNFMKD9KqggakMHSERABknCKDLIkARIIEASCBlIILnj96y699x7hhp21a46p+qcX3XnCebsYe3f2rvW/tfetQsCEIAABCAAAQhAAAIQSBUBRHKq3IExEIAABCAAAQhAAAIQgAAEIFBJAojkStKnbghAAAIQgAAEIAABCEAAAhBIFQFEcqrcgTEQgAAEIAABCEAAAhCAAAQgUEkCiORK0qduCEAAAhCAAAQgAAEIQAACEEgVAURyqtyBMRCAAAQgAAEIQAACEIAABCBQSQKI5ErSp24IQAACEIAABCAAAQhAAAIQSBUBRHKq3IExEIAABCAAAQhAAAIQgAAEIFBJAojkStKnbghAAAIQgAAEIAABCEAAAhBIFQFEcqrcgTEQgAAEIAABCEAAAhCAAAQgUEkCqRLJagwXBCAAAQhAAAIQgAAEIAABCECgUgTyRfJ7770nEydO7DNl1apVsuuuu8qgQYOkoaFB6urqjMys6w6hdjWp/nnsscfko48+MqqARBCAAAQgAAEIQAACEIAABCAAgSQIqD7t6uqSnTt3ypYtW+S8884rn0jWivXP9OnT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" height = "422" width = "750" >
# 

# <a id="6.1"></a> <br>
# ## Confirmed Prediction

# In[ ]:


from keras.layers import Input, Dense, Activation, LeakyReLU, Dropout
from keras import models
from keras.optimizers import RMSprop, Adam
df_confirmed = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_confirmed.csv")
df_confirmed.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mse", #mean_squared_error
#             metrics=["accuracy"]) #metrics.mean_squared_error #mse
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(df_confirmed.iloc[:,5:].sum(axis = 0)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 4500 #2750 #1700 #1800 ! #1800! #
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = False)


# In[ ]:


#model.save("model_confirmed_v1.h5")


# In[ ]:


model_confirmed = models.load_model("/kaggle/input/covid19-models/model_confirmed_v1.h5")
model_confirmed.summary()


# In[ ]:


from datetime import datetime, timedelta,date
lakh = 100000
prediction_days = 10

temp_data = df_confirmed.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_confirmed.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/lakh,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/lakh,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/lakh)+" L\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Confirmed Cases (Lakh)")
plt.title("Next 10 Days Confirmed Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
confirmed_predicted = prediciton_data[length-10:length]


# <a id="6.2"></a> <br>
# ## Death Prediction

# In[ ]:


df_deaths = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_deaths.csv")
df_deaths.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mean_squared_error",
#             metrics=["accuracy"])
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(df_deaths.iloc[:,5:].sum(axis = 0)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 5750 #2600! #2700 #2800! #6000! #5500
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = False)


# In[ ]:


#model.save("model_death_v1.h5")


# In[ ]:


model_death = models.load_model("/kaggle/input/covid19-models/model_death_v1.h5")
model_death.summary()


# In[ ]:


thousand = 1000
prediction_days = 10

temp_data = df_deaths.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_death.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/thousand,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/thousand,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/thousand)+" K\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Death Cases (Thousand)")
plt.title("Next 10 Days Death Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
death_predicted = prediciton_data[length-10:length]


# <a id="6.3"></a> <br>
# ## Recovered Prediction

# In[ ]:


df_recovered = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_recovered.csv")
df_recovered.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mean_squared_error",
#             metrics=["accuracy"])
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(df_recovered.iloc[:,5:].sum(axis = 0)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 7300 #2030 #2359 #2230 #2900 # 8000! #7500
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs)


# In[ ]:


#model.save("model_recovered_v1.h5")


# In[ ]:


model_recovered = models.load_model("/kaggle/input/covid19-models/model_recovered_v1.h5")
model_recovered.summary()


# In[ ]:


from datetime import datetime, timedelta,date
lakh = 100000
prediction_days = 10

temp_data = df_recovered.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_recovered.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/lakh,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/lakh,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/lakh)+" L\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Recovered Cases (Lakh)")
plt.title("Next 10 Days Recoreverd Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# <a id="6.4"></a> <br>
# ## Prediction Table

# In[ ]:


length = len(temp_data)+prediction_days+1
recovered_predicted = prediciton_data[length-10:length]

predicted_table = {"Confirmed(Predicted)":list(np.int64(confirmed_predicted.reshape(-1))),"Deaths(Predicted)":list(np.int64(death_predicted.reshape(-1))),"Recovered(Predicted)":list(np.int64(recovered_predicted.reshape(-1)))}
predicted_table = pd.DataFrame(data = predicted_table)

predicted_table["Death_percentage(predicted)"] = np.round(100*predicted_table["Deaths(Predicted)"]/predicted_table["Confirmed(Predicted)"],2)
predicted_table["Recover_percentage(predicted)"] = np.round(100*predicted_table["Recovered(Predicted)"]/predicted_table["Confirmed(Predicted)"],2)
predicted_table.style.background_gradient(cmap="Blues",subset =["Confirmed(Predicted)"]).background_gradient(cmap="Reds", subset = ["Deaths(Predicted)"]).background_gradient(cmap="Greens", subset = ["Recovered(Predicted)"]).background_gradient(cmap="OrRd", subset = ["Death_percentage(predicted)"]).background_gradient(cmap="BuGn", subset = ["Recover_percentage(predicted)"]).format("{:.0f}",subset = ["Confirmed(Predicted)","Deaths(Predicted)","Recovered(Predicted)"]).format("{:.2f}",subset = ["Death_percentage(predicted)","Recover_percentage(predicted)"])


# * On our **prediction** table it seems like **Covid-19** will be less harmful but more common. If you look at the table **predicted death percentage** is decreasing but **predicted recovered percentage** and **predicted confirmed cases** are increasing in time. 

# <a id="7"></a> <br>
# # LSTM

# In[ ]:


data_lstm = data[["ObservationDate","Confirmed"]]
date_list1 = list(data_lstm["ObservationDate"].unique())
confirmed = []
for i in date_list1:
    x = data_lstm[data_lstm["ObservationDate"] == i]
    confirmed.append(sum(x["Confirmed"]))
data_lstm = pd.DataFrame(list(zip(date_list1,confirmed)),columns = ["Date","Confirmed"])
data_lstm.tail()


# In[ ]:


data_lstm = data_lstm.iloc[:,1].values
data_lstm = data_lstm.reshape(-1,1)
data_lstm = data_lstm.astype("float32")
#data_lstm.shape
df = pd.DataFrame(data_lstm)
df.head()


# In[ ]:


scaler = MinMaxScaler(feature_range = (0, 1))
data_lstm = scaler.fit_transform(data_lstm)


# In[ ]:


train_size = int(len(data_lstm)*0.50)
test_size = len(data_lstm) - train_size
train = data_lstm[0:train_size,:]
test = data_lstm[train_size:len(data_lstm),:]
print("train size: {}, test size: {}".format(len(train),len(test)))


# In[ ]:


time_step = 10 #50
datax = []
datay = []
for i in range(len(test)-time_step-1):
    a = train[i:(i+time_step),0]
    datax.append(a)
    datay.append(test[i + time_step, 0])
trainx = np.array(datax)
trainy = np.array(datay)


# In[ ]:


datax = []
datay = []
for i in range(len(test)-time_step-1):
    a = test[i:(i+time_step),0]
    datax.append(a)
    datay.append(test[i + time_step, 0])
testx = np.array(datax)
testy = np.array(datay)


# In[ ]:


trainx = np.reshape(trainx, (trainx.shape[0], 1 , trainx.shape[1]))
testx = np.reshape(testx, (testx.shape[0], 1 , testx.shape[1]))


# In[ ]:


from keras.layers import Dropout
model = Sequential()
model.add(LSTM(50,return_sequences = True, input_shape =(1,time_step)))
model.add(Dropout(0.1))
model.add(LSTM(50,return_sequences = True))
model.add(Dropout(0.2))
model.add(LSTM(50,return_sequences = True))
model.add(Dropout(0.2))
model.add(LSTM(units = 50))
model.add(Dropout(0.2))
model.add(Dense(1))
model.compile(loss = "mean_squared_error", optimizer="adam")
model.summary()


# In[ ]:


hist = model.fit(trainx,trainy, epochs = 100) #, batch_size = 2)


# In[ ]:


trainPredict = model.predict(trainx)
testPredict = model.predict(testx)

trainPredict = scaler.inverse_transform(trainPredict)
trainy = scaler.inverse_transform([trainy])
testPredict = scaler.inverse_transform(testPredict)
testy = scaler.inverse_transform([testy])

trainScore = math.sqrt(mean_squared_error(trainy[0], trainPredict[:,0]))
print("train score: %.2f RMSE" % (trainScore))
testScore = math.sqrt(mean_squared_error(testy[0], testPredict[:,0]))
print("test score: %.2f RMSE" % (testScore))


# In[ ]:


lstm_loss = hist.history["loss"]
plt.figure(figsize = (13,3))
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Losses-Epochs")
plt.grid(True, alpha = 0.5)
plt.plot(lstm_loss)
plt.show()


# <a id="8"></a> <br>
# # Last 10 Days 

# In[ ]:


data_glob = data_glob.tail(10)
data_glob.tail(10)


# In[ ]:


trace1 = go.Bar(x = data_glob["Confirmed"],
               y = data_glob["Date"],
               orientation = "h",
               text = data_glob["Confirmed"],
               textposition = "auto",
               name = "Confirmed",
               marker = dict(color = "rgba(4,90,141,0.8)"))
                #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace2 = go.Bar(x = data_glob["Deaths"],
               y = data_glob["Date"],
               orientation = "h",
               text = data_glob["Deaths"],
               textposition = "auto",
               name = "Deaths",
               marker = dict(color = "rgba(152,0,67,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace3 = go.Bar(x = data_glob["Recovered"],
               y = data_glob["Date"],
               orientation = "h",
               text = data_glob["Recovered"],
               textposition = "auto",
               name = "Recovered",
               marker = dict(color = "rgba(1,108,89,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))


trace4 = go.Bar(x = data_glob["Active"],
               y = data_glob["Date"],
               orientation = "h",
               text = data_glob["Active"],
               textposition = "auto",
               name = "Active",
               marker = dict(color = "rgba(84,39,143,0.8)"))

data_bar = [trace2,trace4,trace3,trace1]
layout = go.Layout(height = 1000, title = "Last 10 Days", template = "plotly_white",xaxis_title="Value",yaxis_title="Date")
fig = go.Figure(data = data_bar, layout = layout)
iplot(fig)


# In[ ]:


from plotly.subplots import make_subplots

fig = make_subplots(rows=3,cols=1,subplot_titles = ("Death Percentages Last 10 Days","Recovered Percentages Last 10 Days","Active Percentages Last 10 Days"))

death_percent = ((data_glob["Deaths"]*100)/data_glob["Confirmed"])
recovered_percent = ((data_glob["Recovered"]*100)/data_glob["Confirmed"])
active_percent = ((data_glob["Active"]*100)/data_glob["Confirmed"])

fig.append_trace(go.Scatter(x=data_glob["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)')),row = 1, col = 1)

fig.append_trace(go.Scatter(x=data_glob["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)')),row = 2, col = 1)

fig.append_trace(go.Scatter(x=data_glob["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)')),row = 3, col = 1)

fig.update_layout(height = 700,title = "State Percentages Last 10 Days",template="plotly_white",hovermode='x unified')

fig.update_xaxes(title_text="Dates", row=1, col=1)
fig.update_xaxes(title_text="Dates", row=2, col=1)
fig.update_xaxes(title_text="Dates", row=3, col=1)

fig.update_yaxes(title_text="Percentage(%)", row=1, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=2, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=3, col=1)

iplot(fig)


# In[ ]:


trace = go.Bar(
    x = data_glob["Date"],
    y = data_glob["Confirmed"],
    text = data_glob["Confirmed"],
    textposition = "outside",
    marker=dict(color = data_glob["Confirmed"],colorbar=dict(
            title="Colorbar"
        ),colorscale="Blues",))

layout = go.Layout(title = "Confirmed Last 10 Days",template = "plotly_white",yaxis_title="Confirmed",xaxis_title="Date")
fig = go.Figure(data = trace, layout = layout)

iplot(fig)


# In[ ]:


trace = go.Bar(
    x = data_glob["Date"],
    y = data_glob["Deaths"],
    text = data_glob["Deaths"],
    textposition = "outside",
    marker=dict(color = data_glob["Deaths"],colorbar=dict(
            title="Colorbar"
        ),colorscale="Reds",))

layout = go.Layout(title = "Deaths Last 10 Days",template = "plotly_white",yaxis_title="Death",xaxis_title="Date")
fig = go.Figure(data = trace, layout = layout)

iplot(fig)


# In[ ]:


trace = go.Bar(
    x = data_glob["Date"],
    y = data_glob["Recovered"],
    text = data_glob["Recovered"],
    textposition = "outside",
    marker=dict(color = data_glob["Recovered"],colorbar=dict(
            title="Colorbar"
        ),colorscale="YlGn",))

layout = go.Layout(title = "Recovered Last 10 Days",template = "plotly_white",yaxis_title="Recovered",xaxis_title="Date")
fig = go.Figure(data = trace, layout = layout)

iplot(fig)


# In[ ]:


trace = go.Bar(
    x = data_glob["Date"],
    y = data_glob["Active"],
    text = data_glob["Active"],
    textposition = "outside",
    marker=dict(color = data_glob["Active"],colorbar=dict(
            title="Colorbar"
        ),colorscale="Purples",))

layout = go.Layout(title = "Active Last 10 Days",template = "plotly_white",yaxis_title="Active",xaxis_title="Date")
fig = go.Figure(data = trace, layout = layout)

iplot(fig)


# <a id="9"></a> <br>
# # Covid-19 in 3 Big Countries

# <a id="9.1"></a> <br>
# ## 1. China
# * **China:** The country that virus started to spreading.

# <a id="9.11"></a> <br>
# ## Analysis

# In[ ]:


china = data[data["Country/Region"] == "Mainland China"]
china.head()


# In[ ]:


date_list1 = list(china["ObservationDate"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in date_list1:
    x = china[china["ObservationDate"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
china = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
china.head()


# In[ ]:


report_covid_china = china.tail(1)
print("=======China Covid-19 Report=======\nDate: {}\nTotal Confirmed: {}\nTotal Deaths: {}\nTotal Recovered: {}\nTotal Active: {}\n===================================".format(report_covid_china["Date"].iloc[0],int(report_covid_china["Confirmed"].iloc[0]),int(report_covid_china["Deaths"].iloc[0]),int(report_covid_china["Recovered"].iloc[0]),int(report_covid_china["Active"].iloc[0])))


# In[ ]:


trace1 = go.Scatter(
x = china["Date"],
y = china["Confirmed"],
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = china["Date"],
y = china["Deaths"],
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = china["Date"],
y = china["Recovered"],
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = china["Date"],
y = china["Active"],
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "China Case States",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases",legend=dict(
        x=0,
        y=1,),hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)

trace1 = go.Scatter(
x = china["Date"],
y = np.log10(china["Confirmed"]),
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = china["Date"],
y = np.log10(china["Deaths"]),
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = china["Date"],
y = np.log10(china["Recovered"]),
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = china["Date"],
y = np.log10(china["Active"]),
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "China Case States (Log Scale)",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases (Log Scale)",hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)


# In[ ]:


labels = ["Recovered","Deaths","Active"]
values = [china.tail(1)["Recovered"].iloc[0],china.tail(1)["Deaths"].iloc[0],china.tail(1)["Active"].iloc[0]]

fig = go.Figure(data = [go.Pie(labels = labels, values = values,pull = [0.05,0.05,0.05],textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "China Patient Percentage"))
fig.show()


# In[ ]:


death_percent = ((china["Deaths"]*100)/china["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=china["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Death Percentage(%)",title = "China Death Percentage"))
iplot(fig)

recovered_percent = ((china["Recovered"]*100)/china["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=china["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Recovered Percentage(%)",title = "China Recovered Percentage"))
iplot(fig)

active_percent = ((china["Active"]*100)/china["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=china["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Active Percentage(%)",title = "China Active Percentage"))
iplot(fig)


# <a id="9.12"></a> <br>
# ## Prediction 

# <a id="9.121"></a> <br>
# ### Confirmed Prediction

# In[ ]:


df_confirmed = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_confirmed.csv")
china_confirmed = df_confirmed[df_confirmed["Country/Region"] == "China"]
china_confirmed.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mse", #mean_squared_error
#             metrics=["accuracy"]) #metrics.mean_squared_error #mse
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(china_confirmed.iloc[:,5:].sum(axis = 0)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 3600 
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = False)


# In[ ]:


#model.save("model_confirmed_china_v1.h5")


# In[ ]:


model_confirmed_china = models.load_model("/kaggle/input/covid19-models/model_confirmed_china_v1.h5")
model_confirmed_china.summary()


# In[ ]:


from datetime import datetime, timedelta,date
thousand = 10000
prediction_days = 10

temp_data = china_confirmed.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_confirmed_china.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/thousand,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/thousand,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/thousand)+" K\n"

plt.text(0.68, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Confirmed Cases (Thousand)")
plt.title("Next 10 Days Confirmed Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
confirmed_predicted = prediciton_data[length-10:length]


# <a id="9.122"></a> <br>
# ### Death Prediction

# In[ ]:


df_deaths = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_deaths.csv")
china_deaths = df_deaths[df_deaths["Country/Region"] == "China"]
china_deaths.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mean_squared_error",
#             metrics=["accuracy"])
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(china_deaths.iloc[:,5:].sum(axis = 0)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 3000 
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = False)


# In[ ]:


#model.save("model_death_china_v1.h5")


# In[ ]:


model_death_china = models.load_model("/kaggle/input/covid19-models/model_death_china_v1.h5")
model_death_china.summary()


# In[ ]:


thousand = 1000
prediction_days = 10

temp_data = china_deaths.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_death_china.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/thousand,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/thousand,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/thousand)+" K\n"

plt.text(0.68, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Death Cases (Thousand)")
plt.title("Next 10 Days Death Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
death_predicted = prediciton_data[length-10:length]


# <a id="9.123"></a> <br>
# ### Prediction Table

# In[ ]:


length = len(temp_data)+prediction_days+1

predicted_table = {"Confirmed(Predicted)":list(np.int64(confirmed_predicted.reshape(-1))),"Deaths(Predicted)":list(np.int64(death_predicted.reshape(-1)))}
predicted_table = pd.DataFrame(data = predicted_table)

predicted_table["Death_percentage(predicted)"] = np.round(100*predicted_table["Deaths(Predicted)"]/predicted_table["Confirmed(Predicted)"],2)
predicted_table.style.background_gradient(cmap="Blues",subset =["Confirmed(Predicted)"]).background_gradient(cmap="Reds", subset = ["Deaths(Predicted)"]).background_gradient(cmap="OrRd", subset = ["Death_percentage(predicted)"]).format("{:.0f}",subset = ["Confirmed(Predicted)","Deaths(Predicted)"]).format("{:.2f}",subset = ["Death_percentage(predicted)"])


# <a id="9.13"></a> <br>
# ## Last 5 Days

# In[ ]:


china = china.tail(5)
china.head(5)


# In[ ]:


trace1 = go.Bar(x = china["Confirmed"],
               y = china["Date"],
               orientation = "h",
               text = china["Confirmed"],
               textposition = "auto",
               name = "Confirmed",
               marker = dict(color = "rgba(4,90,141,0.8)"))
                #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace2 = go.Bar(x = china["Deaths"],
               y = china["Date"],
               orientation = "h",
               text = china["Deaths"],
               textposition = "auto",
               name = "Deaths",
               marker = dict(color = "rgba(152,0,67,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace3 = go.Bar(x = china["Recovered"],
               y = china["Date"],
               orientation = "h",
               text = china["Recovered"],
               textposition = "auto",
               name = "Recovered",
               marker = dict(color = "rgba(1,108,89,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace4 = go.Bar(x = china["Active"],
               y = china["Date"],
               orientation = "h",
               text = china["Active"],
               textposition = "auto",
               name = "Active",
               marker = dict(color = "rgba(84,39,143,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

data_bar = [trace4,trace2,trace3,trace1]
layout = go.Layout(height = 1000, title = "Last 5 Days in China", template = "plotly_white",yaxis_title="Date",xaxis_title="Value")
fig = go.Figure(data = data_bar, layout = layout)
iplot(fig)


# In[ ]:


fig = make_subplots(rows=3,cols=1,subplot_titles = ("Death Percentages Last 5 Days","Recovered Percentages Last 5 Days","Active Percentages Last 5 Days"))

death_percent = ((china["Deaths"]*100)/china["Confirmed"])
recovered_percent = ((china["Recovered"]*100)/china["Confirmed"])
active_percent = ((china["Active"]*100)/china["Confirmed"])

fig.append_trace(go.Scatter(x=china["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)')),row = 1, col = 1)

fig.append_trace(go.Scatter(x=china["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)')),row = 2, col = 1)

fig.append_trace(go.Scatter(x=china["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)')),row = 3, col = 1)

fig.update_layout(height = 700,title = "State Percentages Last 5 Days",template="plotly_white",hovermode='x unified')

fig.update_xaxes(title_text="Dates", row=1, col=1)
fig.update_xaxes(title_text="Dates", row=2, col=1)
fig.update_xaxes(title_text="Dates", row=3, col=1)

fig.update_yaxes(title_text="Percentage(%)", row=1, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=2, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=3, col=1)

iplot(fig)


# <a id="9.2"></a> <br>
# ## 2. United States (US)
# * **United State (US):** One of the most affected countries and has **most confirmed cases**. 

# <a id="9.21"></a> <br>
# ## Analysis

# In[ ]:


us = data[data["Country/Region"] == "US"]
us.head()


# In[ ]:


date_list1 = list(us["ObservationDate"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in date_list1:
    x = us[us["ObservationDate"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
us = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
us.head()


# In[ ]:


report_covid_us = us.tail(1)
print("=======US Covid-19 Report=======\nDate: {}\nTotal Confirmed: {}\nTotal Deaths: {}\nTotal Recovered: {}\nTotal Active: {}\n================================".format(report_covid_us["Date"].iloc[0],int(report_covid_us["Confirmed"].iloc[0]),int(report_covid_us["Deaths"].iloc[0]),int(report_covid_us["Recovered"].iloc[0]),int(report_covid_us["Active"].iloc[0])))


# In[ ]:


trace1 = go.Scatter(
x = us["Date"],
y = us["Confirmed"],
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = us["Date"],
y = us["Deaths"],
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = us["Date"],
y = us["Recovered"],
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = us["Date"],
y = us["Active"],
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "US Case States",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases",legend=dict(
        x=0,
        y=1,),hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)

trace1 = go.Scatter(
x = us["Date"],
y = np.log10(us["Confirmed"]),
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = us["Date"],
y = np.log10(us["Deaths"]),
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = us["Date"],
y = np.log10(us["Recovered"]),
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = us["Date"],
y = np.log10(us["Active"]),
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "US Case States (Log Scale)",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases (Log Scale)",hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)


# In[ ]:


labels = ["Recovered","Deaths","Active"]
values = [us.tail(1)["Recovered"].iloc[0],us.tail(1)["Deaths"].iloc[0],us.tail(1)["Active"].iloc[0]]

fig = go.Figure(data = [go.Pie(labels = labels, values = values,pull = [0.05,0.05,0.05],textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "US Patient Percentage"))
fig.show()


# In[ ]:


death_percent = ((us["Deaths"]*100)/us["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=us["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Death Percentage(%)",title = "US Death Percentage"))
iplot(fig)

recovered_percent = ((us["Recovered"]*100)/us["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=us["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Recovered Percentage(%)",title = "US Recovered Percentage"))
iplot(fig)

active_percent = ((us["Active"]*100)/us["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=us["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Active Percentage(%)",title = "US Active Percentage"))
iplot(fig)


# <a id="9.22"></a> <br>
# ## Prediction

# <a id="9.221"></a> <br>
# ### Confirmed Prediction

# In[ ]:


df_confirmed = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_confirmed.csv")
us_confirmed = df_confirmed[df_confirmed["Country/Region"] == "US"]
us_confirmed.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mse", #mean_squared_error
#             metrics=["accuracy"]) #metrics.mean_squared_error #mse
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(us_confirmed.iloc[:,5:].sum(axis = 0)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 9200 
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = False)


# In[ ]:


#model.save("model_confirmed_us_v1.h5")


# In[ ]:


model_confirmed_us = models.load_model("/kaggle/input/covid19-models/model_confirmed_us_v1.h5")
model_confirmed_us.summary()


# In[ ]:


from datetime import datetime, timedelta,date
lakh = 100000
prediction_days = 10

temp_data = us_confirmed.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_confirmed_us.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/lakh,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/lakh,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/lakh)+" L\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Confirmed Cases (Thousand)")
plt.title("Next 10 Days Confirmed Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
confirmed_predicted = prediciton_data[length-10:length]


# <a id="9.222"></a> <br>
# ### Death Prediction

# In[ ]:


df_deaths = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_deaths.csv")
us_deaths = df_deaths[df_deaths["Country/Region"] == "US"]
us_deaths.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(80, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "LRelu_l4")(Dense_l4)

#Dense_l5 = Dense(1, name = "Dense_l5")(LRelu_l4)
#LRelu_l5 = LeakyReLU(name = "Output")(Dense_l5)

#model = models.Model(inputs = Visible, outputs = LRelu_l5)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mean_squared_error",
#             metrics=["accuracy"])
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(us_deaths.iloc[:,5:].sum(axis = 0).replace(0,1)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 4700
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = True)


# In[ ]:


#model.save("model_death_us_v1.h5")


# In[ ]:


model_death_us = models.load_model("/kaggle/input/covid19-models/model_death_us_v1.h5")
model_death_us.summary()


# In[ ]:


thousand = 1000
prediction_days = 10

temp_data = us_deaths.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_death_us.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/thousand,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/thousand,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/thousand)+" K\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Death Cases (Thousand)")
plt.title("Next 10 Days Death Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
death_predicted = prediciton_data[length-10:length]


# <a id="9.223"></a> <br>
# ### Prediction Table

# In[ ]:


length = len(temp_data)+prediction_days+1

predicted_table = {"Confirmed(Predicted)":list(np.int64(confirmed_predicted.reshape(-1))),"Deaths(Predicted)":list(np.int64(death_predicted.reshape(-1)))}
predicted_table = pd.DataFrame(data = predicted_table)

predicted_table["Death_percentage(predicted)"] = np.round(100*predicted_table["Deaths(Predicted)"]/predicted_table["Confirmed(Predicted)"],2)
predicted_table.style.background_gradient(cmap="Blues",subset =["Confirmed(Predicted)"]).background_gradient(cmap="Reds", subset = ["Deaths(Predicted)"]).background_gradient(cmap="OrRd", subset = ["Death_percentage(predicted)"]).format("{:.0f}",subset = ["Confirmed(Predicted)","Deaths(Predicted)"]).format("{:.2f}",subset = ["Death_percentage(predicted)"])


# <a id="9.23"></a> <br>
# ## Last 5 Days

# In[ ]:


us = us.tail(5)
us.head(5)


# In[ ]:


trace1 = go.Bar(x = us["Confirmed"],
               y = us["Date"],
               orientation = "h",
               text = us["Confirmed"],
               textposition = "auto",
               name = "Confirmed",
               marker = dict(color = "rgba(4,90,141,0.8)"))
                #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace2 = go.Bar(x = us["Deaths"],
               y = us["Date"],
               orientation = "h",
               text = us["Deaths"],
               textposition = "auto",
               name = "Deaths",
               marker = dict(color = "rgba(152,0,67,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace3 = go.Bar(x = us["Recovered"],
               y = us["Date"],
               orientation = "h",
               text = us["Recovered"],
               textposition = "auto",
               name = "Recovered",
               marker = dict(color = "rgba(1,108,89,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace4 = go.Bar(x = us["Active"],
               y = us["Date"],
               orientation = "h",
               text = us["Active"],
               textposition = "auto",
               name = "Active",
               marker = dict(color = "rgba(84,39,143,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

data_bar = [trace2,trace3,trace4,trace1]
layout = go.Layout(height = 1000, title = "Last 5 Days in US", template = "plotly_white",yaxis_title="Date",xaxis_title="Value")
fig = go.Figure(data = data_bar, layout = layout)
iplot(fig)


# In[ ]:


fig = make_subplots(rows=3,cols=1,subplot_titles = ("Death Percentages Last 5 Days","Recovered Percentages Last 5 Days","Active Percentages Last 5 Days"))

death_percent = ((us["Deaths"]*100)/us["Confirmed"])
recovered_percent = ((us["Recovered"]*100)/us["Confirmed"])
active_percent = ((us["Active"]*100)/us["Confirmed"])

fig.append_trace(go.Scatter(x=us["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)')),row = 1, col = 1)

fig.append_trace(go.Scatter(x=us["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)')),row = 2, col = 1)

fig.append_trace(go.Scatter(x=us["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)')),row = 3, col = 1)

fig.update_layout(height = 700,title = "State Percentages Last 5 Days",template="plotly_white",hovermode='x unified')

fig.update_xaxes(title_text="Dates", row=1, col=1)
fig.update_xaxes(title_text="Dates", row=2, col=1)
fig.update_xaxes(title_text="Dates", row=3, col=1)

fig.update_yaxes(title_text="Percentage(%)", row=1, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=2, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=3, col=1)

iplot(fig)


# <a id="9.3"></a> <br>
# ## 3. United Kingdom (UK)
# * **United Kingdom:** United Kingdom affected very bad from that Covid-19 and has so many death cases. 

# <a id="9.31"></a> <br>
# ## Aalysis

# In[ ]:


uk = data[data["Country/Region"] == "UK"]
uk.head()


# In[ ]:


date_list1 = list(uk["ObservationDate"].unique())
confirmed = []
deaths = []
recovered = []
active = []
for i in date_list1:
    x = uk[uk["ObservationDate"] == i]
    confirmed.append(sum(x["Confirmed"]))
    deaths.append(sum(x["Deaths"]))
    recovered.append(sum(x["Recovered"]))
    active.append(sum(x["Active"]))
uk = pd.DataFrame(list(zip(date_list1,confirmed,deaths,recovered,active)),columns = ["Date","Confirmed","Deaths","Recovered","Active"])
uk.head()


# In[ ]:


report_covid_uk = uk.tail(1)
print("=======UK Covid-19 Report=======\nDate: {}\nTotal Confirmed: {}\nTotal Deaths: {}\nTotal Recovered: {}\nTotal Active: {}\n================================".format(report_covid_uk["Date"].iloc[0],int(report_covid_uk["Confirmed"].iloc[0]),int(report_covid_uk["Deaths"].iloc[0]),int(report_covid_uk["Recovered"].iloc[0]),int(report_covid_uk["Active"].iloc[0])))


# In[ ]:


trace1 = go.Scatter(
x = uk["Date"],
y = uk["Confirmed"],
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = uk["Date"],
y = uk["Deaths"],
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = uk["Date"],
y = uk["Recovered"],
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = uk["Date"],
y = uk["Active"],
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "UK Case States",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases",legend=dict(
        x=0,
        y=1,),hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)

trace1 = go.Scatter(
x = uk["Date"],
y = np.log10(uk["Confirmed"]),
mode = "lines",
name = "Confirmed",
line = dict(width = 2.5),
marker = dict(color = 'rgba(4,90,141, 0.8)')
)

trace2 = go.Scatter(
x = uk["Date"],
y = np.log10(uk["Deaths"]),
mode = "lines",
name = "Deaths",
line = dict(width = 2.5),
marker = dict(color = 'rgba(152,0,67, 0.8)')
)

trace3 = go.Scatter(
x = uk["Date"],
y = np.log10(uk["Recovered"]),
mode = "lines",
name = "Recovered",
line = dict(width = 2.5),    
marker = dict(color = 'rgba(1,108,89, 0.8)')
)

trace4 = go.Scatter(
x = uk["Date"],
y = np.log10(uk["Active"]),
mode = "lines",
name = "Active",
line = dict(width = 2.5),
marker = dict(color = 'rgba(84,39,143, 0.8)')
)

data_plt = [trace1,trace2,trace3,trace4]
layout = go.Layout(title = "UK Case States (Log Scale)",template = "plotly_white",xaxis_title="Date",yaxis_title="Number of Total Cases (Log Scale)",hovermode='x unified')
fig = go.Figure(data = data_plt,layout = layout)

iplot(fig)


# In[ ]:


labels = ["Recovered","Deaths","Active"]
values = [uk.tail(1)["Recovered"].iloc[0],uk.tail(1)["Deaths"].iloc[0],uk.tail(1)["Active"].iloc[0]]

fig = go.Figure(data = [go.Pie(labels = labels, values = values,pull = [0.05,0.05,0.05],textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "UK Patient Percentage"))
fig.show()


# In[ ]:


death_percent = ((uk["Deaths"]*100)/uk["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=uk["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Death Percentage(%)",title = "UK Death Percentage"))
iplot(fig)

recovered_percent = ((uk["Recovered"]*100)/uk["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=uk["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Recovered Percentage(%)",title = "UK Recovered Percentage"))
iplot(fig)

active_percent = ((uk["Active"]*100)/uk["Confirmed"])

fig = go.Figure(data = [go.Scatter(x=uk["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)'))],layout = go.Layout(template = "plotly_white",xaxis_title="Date",yaxis_title="Active Percentage(%)",title = "UK Active Percentage"))
iplot(fig)


# <a id="9.32"></a> <br>
# ## Prediction

# <a id="9.321"></a> <br>
# ### Confirmed Prediction

# In[ ]:


df_confirmed = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_confirmed.csv")
uk_confirmed = df_confirmed[df_confirmed["Country/Region"] == "United Kingdom"]
uk_confirmed.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mse", #mean_squared_error
#             metrics=["accuracy"]) #metrics.mean_squared_error #mse
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(uk_confirmed.iloc[:,5:].sum(axis = 0).replace(0,1)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 4800 #9000!
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = False)


# In[ ]:


#model.save("model_confirmed_uk_v1.h5")


# In[ ]:


model_confirmed_uk = models.load_model("/kaggle/input/covid19-models/model_confirmed_uk_v1.h5")
model_confirmed_uk.summary()


# In[ ]:


from datetime import datetime, timedelta,date
lakh = 100000
prediction_days = 10

temp_data = uk_confirmed.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_confirmed_uk.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/lakh,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/lakh,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/lakh)+" L\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Confirmed Cases (Thousand)")
plt.title("Next 10 Days Confirmed Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
confirmed_predicted = prediciton_data[length-10:length]


# <a id="9.322"></a> <br>
# ### Death Prediction

# In[ ]:


df_deaths = pd.read_csv("/kaggle/input/novel-corona-virus-2019-dataset/time_series_covid_19_deaths.csv")
uk_deaths = df_deaths[df_deaths["Country/Region"] == "United Kingdom"]
uk_deaths.head()


# In[ ]:


#Visible = Input(shape= (1,))
#Dense_l1 = Dense(80, name = "Dense_l1")(Visible)
#LRelu_l1 = LeakyReLU(name = "LRelu_l1")(Dense_l1)

#Dense_l2 = Dense(80, name = "Dense_l2")(LRelu_l1)
#LRelu_l2 = LeakyReLU(name = "LRelu_l2")(Dense_l2)

#Dense_l3 = Dense(80, name = "Dense_l3")(LRelu_l2)
#LRelu_l3 = LeakyReLU(name = "LRelu_l3")(Dense_l3)

#Dense_l4 = Dense(1, name = "Dense_l4")(LRelu_l3)
#LRelu_l4 = LeakyReLU(name = "Output")(Dense_l4)

#model = models.Model(inputs = Visible, outputs = LRelu_l4)
#model.compile(optimizer=Adam(lr = 0.001),
#             loss = "mean_squared_error",
#             metrics=["accuracy"])
#model.summary()


# In[ ]:


data_y = np.log10(np.asarray(uk_deaths.iloc[:,5:].sum(axis = 0).replace(0,1)).astype("float32"))
data_x = np.arange(1, len(data_y)+1)


# In[ ]:


#epochs = 6300 
#model.fit(data_x.reshape([data_y.shape[0],1]),data_y.reshape([data_y.shape[0],1]),epochs = epochs, shuffle = True)


# In[ ]:


#model.save("model_death_uk_v1.h5")


# In[ ]:


model_death_uk = models.load_model("/kaggle/input/covid19-models/model_death_uk_v1.h5")
model_death_uk.summary()


# In[ ]:


thousand = 1000
prediction_days = 10

temp_data = uk_deaths.iloc[:,5:].sum(axis = 0)
prediciton_data = np.power(10,model_death_uk.predict(np.arange(1,len(temp_data)+prediction_days+1)))
f = plt.figure(figsize = (15,10))
ax = f.add_subplot(111)

date = np.arange(0,len(temp_data))

plt.plot(date,temp_data/thousand,color = "darkcyan",marker = "o",markerfacecolor = "#ffffff",label = "Actual Curve")

date = np.arange(0,len(prediciton_data))
plt.plot(date,prediciton_data/thousand,color = "crimson",label = "Predicted Curve")

nextdays = [(datetime.strptime(d[-1],"%d %b")+timedelta(days = i)).strftime("%d %b") for i in range(1,prediction_days+1)]
total = d+nextdays

text = "Prediction for next "+str(prediction_days) + " days:\n"
for i in range(prediction_days):
    text += nextdays[i]+" : "+ str(np.round(prediciton_data[-1*(prediction_days-i)],-3)[0]/thousand)+" K\n"

plt.text(0.02, 0.78, text, fontsize=17, horizontalalignment="left",verticalalignment="top",transform = ax.transAxes,bbox=dict(facecolor = "white", alpha = 0.4))

plt.legend()
plt.xlabel("Days")
plt.ylabel("Number of Death Cases (Thousand)")
plt.title("Next 10 Days Death Prediction")
plt.grid(True, alpha = 0.6 )
plt.show()


# In[ ]:


length = len(temp_data)+prediction_days+1
death_predicted = prediciton_data[length-10:length]


# <a id="9.323"></a> <br>
# ### Prediction Table

# In[ ]:


length = len(temp_data)+prediction_days+1

predicted_table = {"Confirmed(Predicted)":list(np.int64(confirmed_predicted.reshape(-1))),"Deaths(Predicted)":list(np.int64(death_predicted.reshape(-1)))}
predicted_table = pd.DataFrame(data = predicted_table)

predicted_table["Death_percentage(predicted)"] = np.round(100*predicted_table["Deaths(Predicted)"]/predicted_table["Confirmed(Predicted)"],2)
predicted_table.style.background_gradient(cmap="Blues",subset =["Confirmed(Predicted)"]).background_gradient(cmap="Reds", subset = ["Deaths(Predicted)"]).background_gradient(cmap="OrRd", subset = ["Death_percentage(predicted)"]).format("{:.0f}",subset = ["Confirmed(Predicted)","Deaths(Predicted)"]).format("{:.2f}",subset = ["Death_percentage(predicted)"])


# <a id="9.33"></a> <br>
# ## Last 5 Days

# In[ ]:


uk = uk.tail(5)
uk.head(5)


# In[ ]:


trace1 = go.Bar(x = uk["Confirmed"],
               y = uk["Date"],
               orientation = "h",
               text = uk["Confirmed"],
               textposition = "auto",
               name = "Confirmed",
               marker = dict(color = "rgba(4,90,141,0.8)"))
                #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace2 = go.Bar(x = uk["Deaths"],
               y = uk["Date"],
               orientation = "h",
               text = uk["Deaths"],
               textposition = "auto",
               name = "Deaths",
               marker = dict(color = "rgba(152,0,67,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace3 = go.Bar(x = uk["Recovered"],
               y = uk["Date"],
               orientation = "h",
               text = uk["Recovered"],
               textposition = "auto",
               name = "Recovered",
               marker = dict(color = "rgba(1,108,89,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

trace4 = go.Bar(x = uk["Active"],
               y = uk["Date"],
               orientation = "h",
               text = uk["Active"],
               textposition = "auto",
               name = "Active",
               marker = dict(color = "rgba(84,39,143,0.8)"))
                             #,line = dict(color = "rgb(0,0,0)", width = 1.2)))

data_bar = [trace3,trace2,trace4,trace1]
layout = go.Layout(height = 1000, title = "Last 5 Days in UK", template = "plotly_white",yaxis_title="Date",xaxis_title="Value")
fig = go.Figure(data = data_bar, layout = layout)
iplot(fig)


# In[ ]:


fig = make_subplots(rows=3,cols=1,subplot_titles = ("Death Percentages Last 5 Days","Recovered Percentages Last 5 Days","Active Percentages Last 5 Days"))

death_percent = ((uk["Deaths"]*100)/uk["Confirmed"])
recovered_percent = ((uk["Recovered"]*100)/uk["Confirmed"])
active_percent = ((uk["Active"]*100)/uk["Confirmed"])

fig.append_trace(go.Scatter(x=uk["Date"],
                                  y = death_percent,
                                  mode = "lines+markers",
                                  name = "Death Percentage",
                                  marker = dict(color = 'rgba(152,0,67, 0.8)')),row = 1, col = 1)

fig.append_trace(go.Scatter(x=uk["Date"],
                                  y = recovered_percent,
                                  mode = "lines+markers",
                                  name = "Recovered Percentage",
                                  marker = dict(color = 'rgba(1,108,89, 0.8)')),row = 2, col = 1)

fig.append_trace(go.Scatter(x=uk["Date"],
                                  y = active_percent,
                                  mode = "lines+markers",
                                  name = "Active Percentage",
                                  marker = dict(color = 'rgba(84,39,143, 0.8)')),row = 3, col = 1)

fig.update_layout(height = 700,title = "State Percentages Last 5 Days",template="plotly_white",hovermode='x unified')

fig.update_xaxes(title_text="Dates", row=1, col=1)
fig.update_xaxes(title_text="Dates", row=2, col=1)
fig.update_xaxes(title_text="Dates", row=3, col=1)

fig.update_yaxes(title_text="Percentage(%)", row=1, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=2, col=1)
fig.update_yaxes(title_text="Percentage(%)", row=3, col=1)

iplot(fig)


# <a id="10"></a> <br>
# # Patient Data

# In[ ]:


released = patient[patient["state"] == "released"]
isolated = patient[patient["state"] == "isolated"]
deceased = patient[patient["state"] == "deceased"]

fig = make_subplots(rows=4, cols=1,subplot_titles = ("All States Age Frequency","Released Age Frequency","Isolated Age Frequency","Deceased Age Frequency"))

fig.append_trace(go.Histogram(x = patient["age"],
                             name = "All States Age Frequency"),row = 1, col = 1)
fig.append_trace(go.Histogram(x = released["age"],
                             name = "Released Age Frequency"),row = 2, col = 1)
fig.append_trace(go.Histogram(x = isolated["age"],
                             name = "Isolated Age Frequency"),row = 3, col = 1)
fig.append_trace(go.Histogram(x = deceased["age"],
                             name = "Deceased Age Frequency"),row = 4, col = 1)

fig.update_xaxes(title_text="Age", row=1, col=1)
fig.update_xaxes(title_text="Age", row=2, col=1)
fig.update_xaxes(title_text="Age", row=3, col=1)
fig.update_xaxes(title_text="Age", row=4, col=1)

fig.update_yaxes(title_text="Frequency", row=1, col=1)
fig.update_yaxes(title_text="Frequency", row=2, col=1)
fig.update_yaxes(title_text="Frequency", row=3, col=1)
fig.update_yaxes(title_text="Frequency", row=4, col=1)

fig.update_layout(template = "plotly_white",hovermode='x unified',height = 1200)

fig.show()


# In[ ]:


state_list_patient = ["Released","Isolated","Deceased"]

values = [len(released),len(isolated),len(deceased)]

fig = go.Figure(data = [go.Pie(labels = state_list_patient, values = values,pull = [0.1,0.1,0.1],textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Patient State Percentages"))
fig.show()


# * On this chart most of the patients **isolated**(do not forget this data is just a small sample of patients).

# In[ ]:


female = patient[patient["sex"] == "female"]
male = patient[patient["sex"] == "male"]

patient_gender = ["Male","Female"]

values = [len(male),len(female)]

fig = go.Figure(data = [go.Pie(labels = patient_gender, values = values,pull = [0.01,0.01],textinfo='label+percent',insidetextorientation='radial')],layout = go.Layout(title = "Gender Percentages"))
fig.show()


# * On this chart seems like there is not that much difference between male and female.

# In[ ]:


fig = go.Figure(data = [go.Bar(x = ["Released","Isolated","Deceased"],
                       y = [len(released[released["sex"] == "male"]),len(isolated[isolated["sex"] == "male"]),len(deceased[deceased["sex"] == "male"])],
                       name = "Male"),
                       go.Bar(x = ["Released","Isolated","Deceased"],
                               y = [len(released[released["sex"] == "female"]),len(isolated[isolated["sex"] == "female"]),len(deceased[deceased["sex"] == "female"])],
                               name = "Female")],layout = go.Layout(template = "plotly_white", 
                                                                    xaxis_title = "States",
                                                                    yaxis_title = "Number of Patients",
                                                                    title = "State of Patients According to Their Gender",
                                                                    hovermode='x unified'))

fig.show()


# In[ ]:


fig = go.Figure(data = [go.Histogram(x = male["age"],
                            name = "Male",
                            opacity = 1),
                       go.Histogram(x = female["age"],
                            name = "Female",
                            opacity = 1)],
                layout = go.Layout(template = "plotly_white",
                                   hovermode = "x unified",
                                   xaxis_title = "Age", 
                                   yaxis_title = "Frequency",
                                  title = "Age Frequencies According to Gender"))
fig.show()

fig = go.Figure(data = [go.Box(x = male["age"],
                              name = "Male"),
                       go.Box(x = female["age"],
                             name = "Female")],
               layout = go.Layout(template = "plotly_white",
                                  xaxis_title = "Age", 
                                  yaxis_title = "Gender",
                                  title = "Age Boxplots According to Gender"))
fig.show()


# In[ ]:


fig = go.Figure(go.Histogram(x = patient.infection_reason,
                            name = "All"))

fig.update_layout(xaxis={'categoryorder':'total descending'},
                  template = "plotly_white",
                  xaxis_title = "Infection Reason", 
                  yaxis_title = "Frequency",
                  title = "Infection Reasons",
                 hovermode = "x unified")

fig.show()

fig = go.Figure(go.Histogram(x = male.infection_reason,
                            name = "Male"))

fig.update_layout(xaxis={'categoryorder':'total descending'},
                  template = "plotly_white",
                  xaxis_title = "Infection Reason", 
                  yaxis_title = "Frequency",
                  title = "Infection Reasons of Males",
                 hovermode = "x unified")

fig.show()

fig = go.Figure(go.Histogram(x = female.infection_reason))

fig.update_layout(xaxis={'categoryorder':'total descending'},
                  template = "plotly_white",
                  xaxis_title = "Infection Reason", 
                  yaxis_title = "Frequency",
                  title = "Infection Reasons of Females",
                 hovermode = "x unified")

fig.show()


# In[ ]:


fig = px.pie(values = patient.groupby(["infection_reason"]).size().values, 
             names = patient.groupby(["infection_reason"]).size().index)

fig.update_layout(title = "Infection Reasons Piechart")

iplot(fig)


# <a id="11"></a> <br>
# # Covid-19 Classification From Lungs X-Rays
# * Covid-19 is a virus type that has impact on **lungs** so we can find out is a person has Covid-19 or not with **lungs x-rays**. We can use **deep learning** for classifying these x-rays. 

# In[ ]:


DATASET_DIR = "../input/covid-19-x-ray-10000-images/dataset"

os.listdir(DATASET_DIR)


# In[ ]:


normal_images =[]

for img_path in glob.glob(DATASET_DIR + "/normal/*"):
    normal_images.append(mpimg.imread(img_path))
    
fig = plt.figure()
fig.suptitle("Normal Lungs")
plt.imshow(normal_images[0], cmap="gray")
plt.show()


# In[ ]:


covid_images = []
for img_path in glob.glob(DATASET_DIR + "/covid/*"): 
    covid_images.append(mpimg.imread(img_path))
    
fig = plt.figure()
fig.suptitle("Covid-19 Patient's Lungs ")
plt.imshow(covid_images[0], cmap = "gray")
plt.show()


# In[ ]:


print(str(len(normal_images))+" normal patient images")
print(str(len(covid_images))+" covid patient images")


# In[ ]:


IMG_W = 150
IMG_H = 150
CHANNELS = 3

INPUT_SHAPE = (IMG_W, IMG_H, CHANNELS)
NB_CLASSES = 2
EPOCHS = 48
BATCH_SIZE = 6


# <a id="11.1"></a> <br>
# ## CNN Model 
# * To classify images we will use a architecture called **Convolutional Neural Network(CNN)**. This model is mostly using for classify images and so succesful in this area.  
# 
# * **Our model's diagram:**
# <img src="data:image/png;base64,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" height = "422" width = "750" >

# In[ ]:


model = Sequential()
model.add(Conv2D(filters = 32, kernel_size = (3,3), input_shape = INPUT_SHAPE, activation = "relu"))
model.add(MaxPool2D(pool_size = (2,2)))

model.add(Conv2D(filters = 48, kernel_size = (3,3), activation = "relu"))
model.add(MaxPool2D(pool_size = (2,2)))

model.add(Conv2D(filters = 64, kernel_size = (3,3), activation = "relu"))
model.add(MaxPool2D(pool_size = (2,2), strides = (1,1)))
model.add(Dropout(0.25))

#fully connected
model.add(Flatten())
model.add(Dense(32, activation = "relu"))
model.add(Dropout(0.2))
model.add(Dense(1, activation = "sigmoid"))

# compile 
model.compile(loss = "binary_crossentropy",
             optimizer = "rmsprop",
             metrics = ["accuracy"])


# In[ ]:


model.summary()


# In[ ]:


#from tensorflow.keras.utils import plot_model
#plot_model(model)


# <a id="11.2"></a> <br>
# ## Training 

# In[ ]:


#generators
train_datagen = ImageDataGenerator(rescale = 1./255,
                                  shear_range = 0.2,
                                  zoom_range = 0.2,
                                  horizontal_flip = True,
                                  validation_split = 0.25)

train_generator = train_datagen.flow_from_directory(
DATASET_DIR,
target_size = (IMG_H, IMG_W),
batch_size = BATCH_SIZE,
class_mode = "binary",
subset = "training")

validation_generator = train_datagen.flow_from_directory(
DATASET_DIR,
target_size = (IMG_H,IMG_W),
batch_size = BATCH_SIZE,
class_mode ="binary",
shuffle = False,
subset = "validation")

#fitting
hist = model.fit_generator(
train_generator,
steps_per_epoch = train_generator.samples//BATCH_SIZE,
validation_data = validation_generator,
validation_steps = validation_generator.samples // BATCH_SIZE,
epochs = EPOCHS)


# In[ ]:


# model save
model.save("model_cnn_x-ray_v1.h5")


# <a id="11.3"></a> <br>
# ## Result

# In[ ]:


plt.figure(figsize = (13,7))
plt.plot(hist.history["accuracy"])
plt.plot(hist.history["val_accuracy"])
plt.title("Model Accuracy")
plt.ylabel("Accuracy")
plt.xlabel("Epoch")
plt.legend(["Train", "Test"], loc = "upper left")
#plt.text(23,0.5,"Current Training Accuracy: "+str(np.round(hist.history["accuracy"][-1]*100,2))+"%",fontsize = 18,color = "black")
#plt.text(23,0.46,"Current Validation Accuracy: "+str(np.round(hist.history["val_accuracy"][-1]*100,2))+"%",fontsize = 18,color = "black")
plt.show()


# In[ ]:


plt.figure(figsize = (13,7))
plt.plot(hist.history["loss"])
plt.plot(hist.history["val_loss"])
plt.title("Model Loss")
plt.ylabel("Loss")
plt.xlabel("Epoch")
plt.legend(["Train", "Test"], loc = "upper left")
#plt.text(26,0.8,"Current Training Loss: "+str(np.round(hist.history["loss"][-1],3)),fontsize = 18,color = "black")
#plt.text(26,0.73,"Current Validation Loss: "+str(np.round(hist.history["val_loss"][-1],3)),fontsize = 18,color = "black")
plt.show()


# In[ ]:


print("Training Accuracy: "+str(np.round(hist.history["accuracy"][-1]*100,2))+"%")
print("Validation Accuracy: "+str(np.round(hist.history["val_accuracy"][-1]*100,2))+"%")


# In[ ]:


label = validation_generator.classes
pred = model.predict(validation_generator)
predicted_class_indices = np.argmax(pred, axis = 1)
labels = (validation_generator.class_indices)
labels2 = dict((v,k) for k,v in labels.items())
predictions = [labels2[k] for k in predicted_class_indices]
print(predicted_class_indices)
print(labels)
print(predictions)


# In[ ]:


#predicting your images (covid = 0, normal = 1) 

#from tensorflow.keras.preprocessing import image

#def predict_your_images(filepath)
    #img = image.load_img(str(filepath), target_size = (150,150,3))

    #X = image.img_to_array(img)
    #X = np.expand_dims(X, axis = 0)

    #prediction = model.predict(X)
    #if prediction == 0:
    #    print("Covid-19")

    #else: 
    #    print("Normal")

    #plt.imshow(img)
    #plt.show()

    #print(prediction)


# <a id="11.4"></a> <br>
# ## Confusion Matrix

# In[ ]:


from sklearn.metrics import confusion_matrix

cm = confusion_matrix(predicted_class_indices, label)
cm


# In[ ]:


f, ax = plt.subplots(figsize = (8,8))
sns.heatmap(cm,annot = True, linewidths = 0.3,cmap = "Blues",annot_kws = {"size": 18}, linecolor = "black", fmt = ".0f", ax=ax )
plt.xlabel("Prediction")
plt.title("Confusion Matrix")
plt.ylabel("True")
plt.show()


# <a id="12"></a> <br>
# # Conclusion
# * ### If there is something wrong with this kernel please let me know in the comments.
# * ### You can check out my other kernels here: https://www.kaggle.com/mrhippo/notebooks
# * ### I will keep that kernel updated.