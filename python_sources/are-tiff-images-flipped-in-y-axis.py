#!/usr/bin/env python
# coding: utf-8

# In this notebook, I want to show that tiff images are flipped in y-axis. 
# 
# What, I mean is that the index of row 0 correponds to the max latitude and row end 
# to the min latitude

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import rasterio as rio
import folium
import os
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory



# Any results you write to the current directory are saved as output.


# In[ ]:


file = '/kaggle/input/ds4g-environmental-insights-explorer/eie_data/s5p_no2/s5p_no2_20180708T172237_20180714T190743.tif'

image_rio = rio.open(file)


# In[ ]:


print(image_rio.bounds)
[row1,col1] = [0,0]
[row2,col2] = [147,0]
print(image_rio.xy(row1,col1))
print(image_rio.xy(row2,col2))


# Till here, everthing is ok. row=0 corresponds to lattitude min (17.90) and row = 147 corresponds to lattitude max (18.56).

# In[ ]:


[lat, lon] = [18.23, -66.255]
def overlay_image_on_puerto_rico(file,band_layer):
    
    im_rio = rio.open(file)
    
    band = im_rio.read(band_layer)
    
    band[0:10,0:10] = 0
    m = folium.Map([lat, lon], zoom_start=8)
    folium.raster_layers.ImageOverlay(
        image=band,
        bounds = [[17.9 ,-67.3,],[18.6,-65.2]],
        colormap=lambda x: (2, 0, 0, x),
    ).add_to(m)
    [lon0,lat0] = im_rio.xy(0,0)
    folium.Marker([lat0,lon0]).add_to(m)
    return m
overlay_image_on_puerto_rico(file,1)


# In this map, we mark the position of [lon0,lat0] = im_rio.xy(0,0), which corresponds to (col,row)=(0,0). Howerver, when I change the value of the band image (band[0:10,0:10] = 0), it appears in the opposition location.  

# In[ ]:



