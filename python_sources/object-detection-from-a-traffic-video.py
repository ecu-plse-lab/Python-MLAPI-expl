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
for dirname, _, filenames in os.walk('/kaggle/'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 5GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# ## Install pixellib library

# In[ ]:


get_ipython().system(' pip install pixellib')


# ## Download Mask RCNN Coco Weights

# In[ ]:


get_ipython().system('wget --quiet https://github.com/matterport/Mask_RCNN/releases/download/v2.0/mask_rcnn_coco.h5')


# ## Instance Segmentation and Detection from Video

# In[ ]:


import pixellib
from pixellib.instance import instance_segmentation
import cv2

segment_video = instance_segmentation()
segment_video.load_model("mask_rcnn_coco.h5")
segment_video.process_video("/kaggle/input/road-traffic-video-monitoring/traffic_video.avi", show_bboxes = True, frames_per_second= 15, output_video_name="traffic_monitor.mp4")


# ## Output

# #### You can find your output video from the output folder. Here, i have embedded the output from my youtube video. 

# In[ ]:


from IPython.display import HTML
HTML("""
<iframe width="560" height="315" src="https://www.youtube.com/embed/G7FZu0-q0j0" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
""")


# ## If you like this notebook please upvote. Thanks.