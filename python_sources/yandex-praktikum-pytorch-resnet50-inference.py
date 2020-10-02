#!/usr/bin/env python
# coding: utf-8

# ## Yandex Praktikum PyTorch ResNet50 Inference - LB 0.699

# This is inference code for [Yandex Praktikum PyTorch train baseline - LB 0.699](https://www.kaggle.com/alimbekovkz/yandex-praktikum-pytorch-train-baseline-lb-0-699)
# 
# I was inspired thos [code](https://www.kaggle.com/nxrprime/imet-2020-resnet18-inference)

# In[ ]:


import os
import numpy as np 
import pandas as pd 
import json


# In[ ]:


os.listdir('../input/imet-2020-fgvc7')


# In[ ]:


submission = pd.read_csv('../input/imet-2020-fgvc7/sample_submission.csv')
submission.head()


# In[ ]:


# ====================================================
# Library
# ====================================================

import sys

import gc
import os
import random
import time
from contextlib import contextmanager
from pathlib import Path
from collections import defaultdict, Counter

import cv2
from PIL import Image
import numpy as np
import pandas as pd
import scipy as sp

import sklearn.metrics
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold

from functools import partial
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.optim import Adam, SGD
from torch.optim.lr_scheduler import CosineAnnealingLR, ReduceLROnPlateau
from torch.utils.data import DataLoader, Dataset
import torchvision.models as models

from albumentations import Compose, Normalize, Resize, RandomResizedCrop, RandomCrop, HorizontalFlip
from albumentations.pytorch import ToTensorV2

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device


# In[ ]:


# ====================================================
# Utils
# ====================================================

@contextmanager
def timer(name):
    t0 = time.time()
    LOGGER.info(f'[{name}] start')
    yield
    LOGGER.info(f'[{name}] done in {time.time() - t0:.0f} s.')

    
def init_logger(log_file='train.log'):
    from logging import getLogger, DEBUG, FileHandler,  Formatter,  StreamHandler
    
    log_format = '%(asctime)s %(levelname)s %(message)s'
    
    stream_handler = StreamHandler()
    stream_handler.setLevel(DEBUG)
    stream_handler.setFormatter(Formatter(log_format))
    
    file_handler = FileHandler(log_file)
    file_handler.setFormatter(Formatter(log_format))
    
    logger = getLogger('Herbarium')
    logger.setLevel(DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger

LOG_FILE = 'train.log'
LOGGER = init_logger(LOG_FILE)


def seed_torch(seed=777):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True

SEED = 777
seed_torch(SEED)


# In[ ]:


N_CLASSES = 3474


class TrainDataset(Dataset):
    def __init__(self, df, labels, transform=None):
        self.df = df
        self.labels = labels
        self.transform = transform
        
    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        file_name = self.df['id'].values[idx]
        file_path = f'../input/imet-2020-fgvc7/train/{file_name}.png'
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
            
        label = self.labels.values[idx]
        target = torch.zeros(N_CLASSES)
        for cls in label.split():
            target[int(cls)] = 1
        
        return image, target
    

class TestDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df
        self.transform = transform
        
    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        file_name = self.df['id'].values[idx]
        file_path = f'../input/imet-2020-fgvc7/test/{file_name}.png'
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
        
        return image


# In[ ]:


HEIGHT = 128
WIDTH = 128


def get_transforms(*, data):
    
    assert data in ('train', 'valid')
    
    if data == 'train':
        return Compose([
            #Resize(HEIGHT, WIDTH),
            RandomResizedCrop(HEIGHT, WIDTH),
            Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
            ToTensorV2(),
        ])
    
    elif data == 'valid':
        return Compose([
            #Resize(HEIGHT, WIDTH),
            RandomCrop(256, 256),
            HorizontalFlip(p=0.5),
            Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
            ToTensorV2(),
            
        ])


# In[ ]:


batch_size = 128

test_dataset = TestDataset(submission, transform=get_transforms(data='valid'))
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


# In[ ]:


from functools import partial

import torch
from torch import nn
from torch.nn import functional as F
import torchvision.models as M

class AvgPool(nn.Module):
    def forward(self, x):
        return F.avg_pool2d(x, x.shape[2:])

def create_net(net_cls, pretrained: bool):
    if True and pretrained:
        net = net_cls()
        model_name = net_cls.__name__
        weights_path = f'../input/{model_name}/{model_name}.pth'
        net.load_state_dict(torch.load(weights_path))
    else:
        net = net_cls(pretrained=pretrained)
    return net


class ResNet(nn.Module):
    def __init__(self, num_classes,
                 pretrained=False, net_cls=M.resnet50, dropout=False):
        super().__init__()
        self.net = create_net(net_cls, pretrained=pretrained)
        self.net.avgpool = AvgPool()
        if dropout:
            self.net.fc = nn.Sequential(
                nn.Dropout(),
                nn.Linear(self.net.fc.in_features, num_classes),
            )
        else:
            self.net.fc = nn.Linear(self.net.fc.in_features, num_classes)

    def fresh_params(self):
        return self.net.fc.parameters()

    def forward(self, x):
        return self.net(x)


class DenseNet(nn.Module):
    def __init__(self, num_classes,
                 pretrained=False, net_cls=M.densenet121):
        super().__init__()
        self.net = create_net(net_cls, pretrained=pretrained)
        self.avg_pool = AvgPool()
        self.net.classifier = nn.Linear(
            self.net.classifier.in_features, num_classes)

    def fresh_params(self):
        return self.net.classifier.parameters()

    def forward(self, x):
        out = self.net.features(x)
        out = F.relu(out, inplace=True)
        out = self.avg_pool(out).view(out.size(0), -1)
        out = self.net.classifier(out)
        return out


resnet18 = partial(ResNet, net_cls=M.resnet18)
resnet34 = partial(ResNet, net_cls=M.resnet34)
resnet50 = partial(ResNet, net_cls=M.resnet50)
resnet101 = partial(ResNet, net_cls=M.resnet101)
resnet152 = partial(ResNet, net_cls=M.resnet152)

densenet121 = partial(DenseNet, net_cls=M.densenet121)
densenet169 = partial(DenseNet, net_cls=M.densenet169)
densenet201 = partial(DenseNet, net_cls=M.densenet201)
densenet161 = partial(DenseNet, net_cls=M.densenet161)


# In[ ]:


criterion = nn.BCEWithLogitsLoss(reduction='none')
model = resnet50(num_classes=N_CLASSES, pretrained=True)


# In[ ]:


from typing import Dict


# In[ ]:


def load_model(model: nn.Module, path: Path) -> Dict:
    state = torch.load(str(path))
    model.load_state_dict(state['model'])
    print('Loaded model from epoch {epoch}, step {step:,}'.format(**state))
    return state


# In[ ]:


load_model(model, '../input/imet2020/best-model.pt')


# In[ ]:


with timer('inference'):
    
    model.to(device) 
    
    preds = []
    tk0 = tqdm(enumerate(test_loader), total=len(test_loader))

    for i, images in tk0:
            
        images = images.to(device)
            
        with torch.no_grad():
            y_preds = model(images)
            
        preds.append(torch.sigmoid(y_preds).to('cpu').numpy())


# In[ ]:


threshold = 0.10
predictions = np.concatenate(preds) > threshold

for i, row in enumerate(predictions):
    ids = np.nonzero(row)[0]
    submission.iloc[i].attribute_ids = ' '.join([str(x) for x in ids])
    
submission.to_csv('submission.csv', index=False)
submission.head()


# In[ ]:



