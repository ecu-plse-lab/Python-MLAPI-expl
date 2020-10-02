#!/usr/bin/env python
# coding: utf-8

# For the general context, see  also:
# 
# * A deepsense.ai blog post [Keras vs. PyTorch - Alien vs. Predator recognition with transfer learning](https://deepsense.ai/keras-vs-pytorch-avp-transfer-learning) in which we compare and contrast Keras and PyTorch approaches.
# * Repo with code: [github.com/deepsense-ai/Keras-PyTorch-AvP-transfer-learning](https://github.com/deepsense-ai/Keras-PyTorch-AvP-transfer-learning).
# * Free event: [upcoming webinar (10 Oct 2018)](https://www.crowdcast.io/e/KerasVersusPyTorch/register), in which we walk trough the code (and you will be able to ask questions).
# 
# ### 1. Import dependencies

# In[ ]:


import numpy as np
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
from PIL import Image


# In[ ]:


import torch
from torchvision import datasets, models, transforms
import torch.nn as nn
from torch.nn import functional as F
import torch.optim as optim


# In[ ]:


torch.__version__  # should be 0.4.1


# In[ ]:


import torchvision
torchvision.__version__  # should be 0.2.1


# In[ ]:


# Kaggle Kernel-dependent
input_path = "../input/alien_vs_predator_thumbnails/data/"


# ### 2. Create PyTorch data generators

# In[ ]:


normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

data_transforms = {
    'train':
    transforms.Compose([
        transforms.Resize((224,224)),
        transforms.RandomAffine(0, shear=10, scale=(0.8,1.2)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        normalize
    ]),
    'validation':
    transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        normalize
    ]),
}

image_datasets = {
    'train': 
    datasets.ImageFolder(input_path + 'train', data_transforms['train']),
    'validation': 
    datasets.ImageFolder(input_path + 'validation', data_transforms['validation'])
}

dataloaders = {
    'train':
    torch.utils.data.DataLoader(image_datasets['train'],
                                batch_size=32,
                                shuffle=True,
                                num_workers=0),  # for Kaggle
    'validation':
    torch.utils.data.DataLoader(image_datasets['validation'],
                                batch_size=32,
                                shuffle=False,
                                num_workers=0)  # for Kaggle
}


# ### 3. Create the network

# In[ ]:


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device


# In[ ]:


model = models.resnet50(pretrained=True).to(device)
    
for param in model.parameters():
    param.requires_grad = False   
    
model.fc = nn.Sequential(
               nn.Linear(2048, 128),
               nn.ReLU(inplace=True),
               nn.Linear(128, 2)).to(device)


# In[ ]:


criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters())


# ### 4. Train the model

# In[ ]:


def train_model(model, criterion, optimizer, num_epochs=3):
    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch+1, num_epochs))
        print('-' * 10)

        for phase in ['train', 'validation']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

            running_loss = 0.0
            running_corrects = 0

            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                if phase == 'train':
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                _, preds = torch.max(outputs, 1)
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)

            epoch_loss = running_loss / len(image_datasets[phase])
            epoch_acc = running_corrects.double() / len(image_datasets[phase])

            print('{} loss: {:.4f}, acc: {:.4f}'.format(phase,
                                                        epoch_loss,
                                                        epoch_acc))
    return model


# There is some error (even though the same version work on my own computer):
# 
# > RuntimeError: DataLoader worker (pid 56) is killed by signal: Bus error. Details are lost due to multiprocessing. Rerunning with num_workers=0 may give better error trace.
# > RuntimeError: DataLoader worker (pid 59) exited unexpectedly with exit code 1. Details are lost due to multiprocessing. Rerunning with num_workers=0 may give better error trace.
#  
# See [this issue](https://github.com/pytorch/pytorch/issues/5301) and [that thread](https://discuss.pytorch.org/t/dataloader-randomly-crashes-after-few-epochs/20433/2). Setting `num_workers=0` in `DataLoader` solved it.

# In[ ]:


model_trained = train_model(model, criterion, optimizer, num_epochs=3)


# ### 5. Save and load the model

# In[ ]:


get_ipython().system('mkdir models')
get_ipython().system('mkdir models/pytorch')


# In[ ]:


torch.save(model_trained.state_dict(), 'models/pytorch/weights.h5')


# In[ ]:


model = models.resnet50(pretrained=False).to(device)
model.fc = nn.Sequential(
               nn.Linear(2048, 128),
               nn.ReLU(inplace=True),
               nn.Linear(128, 2)).to(device)
model.load_state_dict(torch.load('models/pytorch/weights.h5'))


# ### 6. Make predictions on sample test images

# In[ ]:


validation_img_paths = ["validation/alien/11.jpg",
                        "validation/alien/22.jpg",
                        "validation/predator/33.jpg"]
img_list = [Image.open(input_path + img_path) for img_path in validation_img_paths]


# In[ ]:


validation_batch = torch.stack([data_transforms['validation'](img).to(device)
                                for img in img_list])


# In[ ]:


pred_logits_tensor = model(validation_batch)
pred_logits_tensor


# In[ ]:


pred_probs = F.softmax(pred_logits_tensor, dim=1).cpu().data.numpy()
pred_probs


# In[ ]:


fig, axs = plt.subplots(1, len(img_list), figsize=(20, 5))
for i, img in enumerate(img_list):
    ax = axs[i]
    ax.axis('off')
    ax.set_title("{:.0f}% Alien, {:.0f}% Predator".format(100*pred_probs[i,0],
                                                            100*pred_probs[i,1]))
    ax.imshow(img)


# In[ ]:



