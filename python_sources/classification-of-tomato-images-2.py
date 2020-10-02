#!/usr/bin/env python
# coding: utf-8

# [Google Colaboratory Variant](https://colab.research.google.com/drive/1pymaadPUhSm0T9N5h44ls-mAcrylfa2F)
# ## Code Modules & Functions

# In[ ]:


get_ipython().system('pip install --upgrade neural_structured_learning --user')


# In[ ]:


import warnings; warnings.filterwarnings('ignore')
import pandas as pd,numpy as np
import tensorflow_hub as th,tensorflow as tf
import neural_structured_learning as nsl
import os,pylab as pl
from keras.preprocessing import image as kimage
from tqdm import tqdm
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES=True 
fpath='../input/tomato-cultivars/'


# In[ ]:


def path_to_tensor(img_path,fpath=fpath):
    img=kimage.load_img(fpath+img_path, 
                        target_size=(160,160))
    x=kimage.img_to_array(img)
    return np.expand_dims(x,axis=0)
def paths_to_tensor(img_paths):
    tensor_list=[path_to_tensor(img_path) 
                 for img_path in tqdm(img_paths)]
    return np.vstack(tensor_list)


# ## Data

# In[ ]:


names=['Kumato','Beefsteak','Tigerella',
       'Roma','Japanese Black Trifele',
       'Yellow Pear','Sun Gold','Green Zebra',
       'Cherokee Purple','Oxheart','Blue Berries',
       'San Marzano','Banana Legs',
       'German Orange Strawberry','Supersweet 100']
flist=sorted(os.listdir(fpath))
labels=np.array([int(el[:2]) for el in flist],
               dtype='float32')-1
images=np.array(paths_to_tensor(flist),
                dtype='float32')/255
N=labels.shape[0]; n=int(.1*N)
shuffle_ids=np.arange(N)
np.random.RandomState(12).shuffle(shuffle_ids)
images,labels=images[shuffle_ids],labels[shuffle_ids]
x_test,x_valid,x_train=images[:n],images[n:2*n],images[2*n:]
y_test,y_valid,y_train=labels[:n],labels[n:2*n],labels[2*n:]


# In[ ]:


set(labels)


# In[ ]:


pd.DataFrame([[x_train.shape,x_valid.shape,x_test.shape],
              [x_train.dtype,x_valid.dtype,x_test.dtype],
              [y_train.shape,y_valid.shape,y_test.shape],
              [y_train.dtype,y_valid.dtype,y_test.dtype]],               
             columns=['train','valid','test'])


# In[ ]:


k=np.random.randint(40)
print('Label: ',y_test[k],
      names[int(y_test[k])])
pl.figure(figsize=(3,3))
pl.imshow((x_test[k]));


# ## NN Examples

# In[ ]:


fw='weights.best.hdf5'
def premodel(pix,den,mh,lbl,activ,loss):
    model=tf.keras.Sequential([
        tf.keras.layers.Input((pix,pix,3),
                              name='input'),
        th.KerasLayer(mh,trainable=True),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(den,activation='relu'),
        tf.keras.layers.Dropout(rate=.5),
        tf.keras.layers.Dense(lbl,activation=activ)])
    model.compile(optimizer='adam',
                  metrics=['accuracy'],loss=loss)
    display(model.summary())
    return model
def cb(fw):
    early_stopping=tf.keras.callbacks    .EarlyStopping(monitor='val_loss',patience=20,verbose=2)
    checkpointer=tf.keras.callbacks    .ModelCheckpoint(filepath=fw,save_best_only=True,verbose=2)
    lr_reduction=tf.keras.callbacks    .ReduceLROnPlateau(monitor='val_loss',verbose=2,
                       patience=5,factor=.8)
    return [checkpointer,early_stopping,lr_reduction]


# In[ ]:


[handle_base,pixels]=["inception_v3",160]
mhandle="https://tfhub.dev/google/imagenet/{}/classification/4".format(handle_base)


# In[ ]:


model=premodel(pixels,1024,mhandle,15,
               'softmax','sparse_categorical_crossentropy')
history=model.fit(x=x_train,y=y_train,batch_size=32,
                  epochs=70,callbacks=cb(fw),
                  validation_data=(x_valid,y_valid))


# In[ ]:


model.load_weights(fw)
model.evaluate(x_test,y_test)


# In[ ]:


[handle_base,pixels]=["mobilenet_v2_100_160",160]
mhandle="https://tfhub.dev/google/imagenet/{}/classification/4".format(handle_base)


# In[ ]:


model=premodel(pixels,1024,mhandle,15,
               'softmax','sparse_categorical_crossentropy')
history=model.fit(x=x_train,y=y_train,batch_size=32,
                  epochs=70,callbacks=cb(fw),
                  validation_data=(x_valid,y_valid))


# In[ ]:


model.load_weights(fw)
model.evaluate(x_test,y_test)


# In[ ]:


batch_size=64; img_size=x_train.shape[1]; epochs=30
base_model=tf.keras.Sequential([
    tf.keras.Input((img_size,img_size,3),name='input'),
    tf.keras.layers.Conv2D(32,(5,5),padding='same'),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.Conv2D(196,(5,5)),
    tf.keras.layers.Activation('relu'),    
    tf.keras.layers.MaxPooling2D(pool_size=(2,2)),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.GlobalMaxPooling2D(),    
    tf.keras.layers.Dense(512),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.Dense(128),
    tf.keras.layers.Activation('relu'),
    tf.keras.layers.Dropout(.25),
    tf.keras.layers.Dense(15,activation='softmax')
])
adv_config=nsl.configs.make_adv_reg_config(multiplier=.2,adv_step_size=.05)
adv_model=nsl.keras.AdversarialRegularization(base_model,adv_config=adv_config)
adv_model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])


# In[ ]:


train=tf.data.Dataset.from_tensor_slices(
    {'input':x_train,'label':y_train})\
     .batch(batch_size)
valid=tf.data.Dataset.from_tensor_slices(
    {'input':x_valid,'label':y_valid})\
     .batch(batch_size)
valid_steps=x_valid.shape[0]//batch_size
adv_model.fit(train,validation_data=valid,verbose=2,
              validation_steps=valid_steps,epochs=epochs)


# In[ ]:


adv_model.evaluate({'input':x_test,'label':y_test})
