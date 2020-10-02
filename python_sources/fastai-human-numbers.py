#!/usr/bin/env python
# coding: utf-8

# **Human Numbers**

# In[ ]:


get_ipython().run_line_magic('reload_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


from fastai.text import *


# In[ ]:


bs=64


# In[ ]:


path = untar_data(URLs.HUMAN_NUMBERS)
path.ls()


# In[ ]:


def readnums(d): return [', '.join(o.strip() for o in open(path/d).readlines())]


# In[ ]:


train_txt = readnums('train.txt'); train_txt[0][:80]


# In[ ]:


#valid_txt = readnums('valid.txt'); valid_txt[0][-80:]
valid_txt = readnums('valid.txt'); valid_txt[0][:80]


# In[ ]:


train = TextList(train_txt, path=path)
valid = TextList(valid_txt, path=path)

src = ItemLists(path=path, train=train, valid=valid).label_for_lm()
data = src.databunch(bs=bs)


# In[ ]:


train[0].text[:80]


# In[ ]:


valid[0].text[:80]


# In[ ]:


len(data.valid_ds[0][0].data)


# In[ ]:


data.valid_ds[0][0]


# In[ ]:


data.bptt, len(data.valid_dl)


# In[ ]:


13017/70/bs


# In[ ]:


data.valid_ds[0][0].data


# In[ ]:


it = iter(data.valid_dl)
x1,y1 = next(it)
x2,y2 = next(it)
x3,y3 = next(it)
it.close()


# In[ ]:


x1


# In[ ]:


y1


# In[ ]:


x1.numel()+x2.numel()+x3.numel()


# In video this comes out to be less, 12928

# In[ ]:


x1.shape,y1.shape


# Again came out to be 95,64 and he was looking for something around 70,64

# In[ ]:


x2.shape,y2.shape


# Video Lecture : 69,64

# In[ ]:


#x1[:,0]
x1[0]


# In[ ]:


#y1[:,0]
y1[0]


# https://github.com/fastai/course-v3/issues/257

# In[ ]:


v = data.valid_ds.vocab


# In[ ]:


v.textify(x1[0])


# In[ ]:


v.textify(y1[0])


# In[ ]:


v.textify(x2[0])


# In[ ]:


v.textify(x3[0])


# In[ ]:


v.textify(x1[1])


# In[ ]:


v.textify(x2[1])


# In[ ]:


v.textify(x3[1])


# In[ ]:


v.textify(x3[-1])


# In[ ]:


data.show_batch(ds_type=DatasetType.Valid)


# Single Fully Connected Model

# In[ ]:


data = src.databunch(bs=bs, bptt=3)


# In[ ]:


x,y = data.one_batch()
x.shape,y.shape


# In[ ]:


v.itos


# In[ ]:


nv = len(v.itos); nv


# In[ ]:


nh=64


# In[ ]:


def loss4(input,target): return F.cross_entropy(input, target[:,-1])
def acc4 (input,target): return accuracy(input, target[:,-1])


# In[ ]:


class Model0(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_h = nn.Embedding(nv,nh)  # green arrow
        self.h_h = nn.Linear(nh,nh)     # brown arrow
        self.h_o = nn.Linear(nh,nv)     # blue arrow
        self.bn = nn.BatchNorm1d(nh)
        
    def forward(self, x):
        h = self.bn(F.relu(self.h_h(self.i_h(x[:,0]))))
        if x.shape[1]>1:
            h = h + self.i_h(x[:,1])
            h = self.bn(F.relu(self.h_h(h)))
        if x.shape[1]>2:
            h = h + self.i_h(x[:,2])
            h = self.bn(F.relu(self.h_h(h)))
        return self.h_o(h)


# In[ ]:


learn = Learner(data, Model0(), loss_func=loss4, metrics=acc4)


# In[ ]:


learn.fit_one_cycle(6, 1e-4)


# Same thing with a loop

# In[ ]:


class Model1(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_h = nn.Embedding(nv,nh)  # green arrow
        self.h_h = nn.Linear(nh,nh)     # brown arrow
        self.h_o = nn.Linear(nh,nv)     # blue arrow
        self.bn = nn.BatchNorm1d(nh)
        
    def forward(self, x):
        h = torch.zeros(x.shape[0], nh).to(device=x.device)
        for i in range(x.shape[1]):
            h = h + self.i_h(x[:,i])
            h = self.bn(F.relu(self.h_h(h)))
        return self.h_o(h)


# In[ ]:


learn = Learner(data, Model1(), loss_func=loss4, metrics=acc4)


# In[ ]:


learn.fit_one_cycle(6, 1e-4)


# Multi Fully connected Model

# In[ ]:


data = src.databunch(bs=bs, bptt=20)


# In[ ]:


x,y = data.one_batch()
x.shape,y.shape


# In[ ]:


class Model2(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_h = nn.Embedding(nv,nh)
        self.h_h = nn.Linear(nh,nh)
        self.h_o = nn.Linear(nh,nv)
        self.bn = nn.BatchNorm1d(nh)
        
    def forward(self, x):
        h = torch.zeros(x.shape[0], nh).to(device=x.device)
        res = []
        for i in range(x.shape[1]):
            h = h + self.i_h(x[:,i])
            h = F.relu(self.h_h(h))
            res.append(self.h_o(self.bn(h)))
        return torch.stack(res, dim=1)


# In[ ]:


learn = Learner(data, Model2(), metrics=accuracy)


# In[ ]:


learn.fit_one_cycle(10, 1e-4, pct_start=0.1)


# Main State

# In[ ]:


class Model3(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_h = nn.Embedding(nv,nh)
        self.h_h = nn.Linear(nh,nh)
        self.h_o = nn.Linear(nh,nv)
        self.bn = nn.BatchNorm1d(nh)
        self.h = torch.zeros(bs, nh).cuda()
        
    def forward(self, x):
        res = []
        h = self.h
        for i in range(x.shape[1]):
            h = h + self.i_h(x[:,i])
            h = F.relu(self.h_h(h))
            res.append(self.bn(h))
        self.h = h.detach()
        res = torch.stack(res, dim=1)
        res = self.h_o(res)
        return res


# In[ ]:


learn = Learner(data, Model3(), metrics=accuracy)


# In[ ]:


learn.fit_one_cycle(20, 3e-3)


# nn.RNN

# In[ ]:


class Model4(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_h = nn.Embedding(nv,nh)
        self.rnn = nn.RNN(nh,nh, batch_first=True)
        self.h_o = nn.Linear(nh,nv)
        self.bn = BatchNorm1dFlat(nh)
        self.h = torch.zeros(1, bs, nh).cuda()
        
    def forward(self, x):
        res,h = self.rnn(self.i_h(x), self.h)
        self.h = h.detach()
        return self.h_o(self.bn(res))


# In[ ]:


learn = Learner(data, Model4(), metrics=accuracy)


# In[ ]:


learn.fit_one_cycle(20, 3e-3)


# **2-Layer GRU**

# In[ ]:


class Model5(nn.Module):
    def __init__(self):
        super().__init__()
        self.i_h = nn.Embedding(nv,nh)
        self.rnn = nn.GRU(nh, nh, 2, batch_first=True)
        self.h_o = nn.Linear(nh,nv)
        self.bn = BatchNorm1dFlat(nh)
        self.h = torch.zeros(2, bs, nh).cuda()
        
    def forward(self, x):
        res,h = self.rnn(self.i_h(x), self.h)
        self.h = h.detach()
        return self.h_o(self.bn(res))


# In[ ]:


learn = Learner(data, Model5(), metrics=accuracy)


# In[ ]:


learn.fit_one_cycle(10, 1e-2)
