#!/usr/bin/env python
# coding: utf-8

# **Before you fork, please support and upvote!**

# # Prostate cANcer graDe Assessment (PANDA) Challenge
# 
# 
# 

# Versions:
# 
# 1.First run, didn't work because inference had error
# 
# 2.First successful run - LB: 0.59
# 
# 3.Added TTA - LB: 0.63
# 
# 4.Tried mixup - LB: 0.62
# 
# 6.Tried label smoothing - LB: 0.67
# 
# 9.Try larger model(SE-ResNext101) - LB: 0.66
# 
# 10.Added 5-fold CV training

# 
# ## Introduction
# Prostate cancer is the [most common cancer in males in the United States](https://gis.cdc.gov/Cancer/USCS/DataViz.html) and [most common cancer in men worldwide](https://www.wcrf.org/dietandcancer/cancer-trends/worldwide-cancer-data). 
# 
# Diagnosis _and prognosis_ is based on [histology](https://en.wikipedia.org/wiki/Histology) analysis of prostate samples taken via biopsy. The tissue samples are scored by pathologists with the [Gleason grading system](https://en.wikipedia.org/wiki/Gleason_grading_system) ([developed](https://www.ncbi.nlm.nih.gov/pubmed/5948714) by Dr. Donald Gleason in 1966). Cancers with higher Gleason score are more aggressive and have a worse prognosis.
# 
# ![image.png](attachment:image.png)
# 
# The Gleason score is based on the identificatio of Gleason "patterns" in the biopsy specimen. A primary and secondary grade is assigned, which is based on the dominant, and the next-most frequent patterns, respectively. The final Gleason score is a sum of these two, such as `7 (3+4)`. The individual Gleason grades can technically vary from 1 to 5, but Gleason grades 1 and 2 are discontinued as they do not differ in outcome from grade 3.
# 
# In 2014, the International Society of Urological Pathology (ISUP) suggested a new 5-grade system for combining the primary and secondary Gleason grades:
# 
# ![image.png](data:image/jpeg;base64,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)
# 
# A major problem with the Gleason grading scale is inter-pathologist variability ([here](https://www.ncbi.nlm.nih.gov/pubmed/21146858) and [here](https://www.ncbi.nlm.nih.gov/pubmed/27416104)). This variability of diagnosis could result in unnecessary treatment of missing severe cases. Therefore, deep learning has an opportunity to automate and improve the objectivity of the grading. Such deep learning systems to augment the pathologist's workflow and decrease the overall workload.
# 
# Several systems have already been developed. This includes some work by [Google](https://ai.googleblog.com/2018/11/improved-grading-of-prostate-cancer.html), as well as [some work](https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(19)30739-9/fulltext) from the competition organizers. However, the major difference with this challenge is the use of a multi-center extensive dataset, that is the largest public whole-slide image dataset available. 
# 
# Clearly this is an important problem, and I am excited to work this this unique dataset.
# 
# ## A look at the data
# 
# There is a detailed report of the PANDA challenge dataset available [here](https://zenodo.org/record/3715938#.XqPQe2hKhEa).
# 
# > Your challenge in this competition is to classify the severity of prostate cancer from microscopy scans of prostate biopsy samples. There are two unusual twists to this problem relative to most competitions:
# > 
# > Each individual image is quite large. We're excited to see what strategies you come up with for efficiently locating areas of concern to zoom in on.
# > 
# > The labels are imperfect. This is a challenging area of pathology and even experts in the field with years of experience do not always agree on how to interpret a slide. This will make training models more difficult, but increases the potential medical value of having a strong model to provide consistent ratings. All of the private test set images and most of the public test set images were graded by multiple pathologists, but this was not feasible for the training set. You can find additional details about how consistently the pathologist's labels matched here.
# 
# 
# In the train.csv file, the `data_provider` (Karolinska Institute or Radboud University Medical Center), `isup_grade` (the target, only provided in train), and the `gleason_score` (train only) is provided.
# 
# Whole-slide images are often digitally saved as multi-level TIFF files. This is the case for the images here: 10616 train images, and ~1000 test images.
# 
# Let's analyze the images a little further.

# In[ ]:


get_ipython().run_line_magic('reload_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


import openslide
import os
from PIL import Image
import pandas as pd
import numpy as np


# # Quick and dirty EDA:

# Let's check out our csv file and the labels:

# In[ ]:


train_df = pd.read_csv('../input/prostate-cancer-grade-assessment/train.csv')


# In[ ]:


train_df.head(10)


# In[ ]:


len_df = len(train_df)
print(f"There are {len_df} train images")


# In[ ]:


train_df['isup_grade'].hist(figsize = (10, 5))


# The labels are somewhat imbalanced, with no cancer and the least aggressive version, being the most common labels.
# 
# Let's look at the individual Gleason pattern scores:

# In[ ]:


train_df[['primary Gleason', 'secondary Gleason']] = train_df.gleason_score.str.split('+',expand=True)


# In[ ]:


train_df[['primary Gleason', 'secondary Gleason']]


# In[ ]:


train_df['primary Gleason'].hist(figsize = (10, 5))


# In[ ]:


train_df['secondary Gleason'].hist(figsize = (10, 5))


# Here, we see that the Gleason pattern 3 is the most common.
# 
# Now let's check some example images. We can use [OpenSlide](https://openslide.org/) as an interface to open and display these whole-slide images:

# In[ ]:


ex_img_path = '../input/prostate-cancer-grade-assessment/train_images/'+train_df['image_id'][np.random.choice(len(train_df))]+'.tiff'
example_image = openslide.OpenSlide(ex_img_path)


# OpenSlide provides a lot of information about the file properties:

# In[ ]:


example_image.properties


# Here we can see that the images have 3 levels, and the sizes of those levels are shown. The first level is the full-resolution image, and the subsequent ones are downsampled versions. We will work with level 3, the most downsampled version.

# In[ ]:


img = example_image.read_region(location=(0,0),level=2,size=(example_image.level_dimensions[2][0],example_image.level_dimensions[2][1]))
print(img.size)
img


# You can use the `read_region` function to read patches of the image without loading the whole image into memory.
# 
# These images are quite large, even though they are downsampled. We will use a 512x512-resized version of the dataset that I generated [here](https://www.kaggle.com/tanlikesmath/panda-challenge-512x512-resized-dataset/). If you want a 256x256 version, please see [here](https://www.kaggle.com/tanlikesmath/panda-challenge-256x256-resized-dataset/). Please upvote these kernels if you find them helpful. Note that this kernel is using the output of these other kernels. This is a great alternative to creating datasets in my opinion, and it allows you to save dataset storage space ;)
# 
# Now that we understand the problem and the dataset, we can create a simple baseline, which, as we will see, performs pretty well.

# ## fastai2 training baseline

# Note that no internet connection is allowed.
# 
# Let's install [fastai2](https://github.com/fastai/fastai2) and [pretrainedmodels](https://github.com/Cadene/pretrained-models.pytorch) and its dependencies:

# In[ ]:


get_ipython().system('pip install /kaggle/input/fastai2-wheels/fastscript-0.1.4-py3-none-any.whl > /dev/null')
get_ipython().system('pip install /kaggle/input/fastai2-wheels/kornia-0.2.0-py2.py3-none-any.whl > /dev/null')
get_ipython().system('pip install /kaggle/input/fastai2-wheels/nbdev-0.2.12-py3-none-any.whl > /dev/null')
get_ipython().system('pip install /kaggle/input/fastai2-wheels/fastprogress-0.2.3-py3-none-any.whl > /dev/null')
get_ipython().system('pip install /kaggle/input/fastai2-wheels/fastcore-0.1.16-py3-none-any.whl > /dev/null')
get_ipython().system('pip install /kaggle/input/fastai2-wheels/fastai2-0.0.16-py3-none-any.whl > /dev/null')
get_ipython().system('pip install ../input/pretrainedmodels/pretrainedmodels-0.7.4/pretrainedmodels-0.7.4/ > /dev/null')


# In[ ]:


from fastai2.vision.all import *
import pretrainedmodels


# Let's move the SE-ResNext model weights to the appropriate location for PyTorch to find.

# In[ ]:


# Making pretrained weights work without needing to find the default filename
if not os.path.exists('/root/.cache/torch/checkpoints/'):
        os.makedirs('/root/.cache/torch/checkpoints/')
get_ipython().system("cp '../input/pytorch-se-resnext/se_resnext50_32x4d-a260b3a4.pth' '/root/.cache/torch/checkpoints/se_resnext50_32x4d-a260b3a4.pth'")


# Always seed everything! :)

# In[ ]:


def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True

SEED = 999
seed_everything(SEED)


# In fastai2, you define a "template" for how to process your data. This is known as a DataBlock. Here we define our DataBlock to use the image files defined in the column `image_id`, and use the labels defined in the column `isup_grade`. The images are resized (meaningless for now since already at 512), and augmentation is performed on the GPU.

# In[ ]:


train_df['image_id'] = '../input/panda-challenge-512x512-resized-dataset/' + train_df['image_id']


# In[ ]:


panda_block = DataBlock(blocks=(ImageBlock, CategoryBlock),
                        splitter=RandomSplitter(),
                        get_x=ColReader('image_id',suff='.jpeg'),
                        get_y=ColReader('isup_grade'),
                        item_tfms=Resize(512),
                        batch_tfms=aug_transforms()
                       )


# With our Data Block defined, we can create train and valid DataLoaders with all the information in the `train_df`.

# In[ ]:


dls = panda_block.dataloaders(train_df,bs=16)


# Let's view an example batch. If this does not succeed and there is an error in your code, you can use `panda_block.summary(train_df)` to print out the entire pipeline and debug your code.

# In[ ]:


dls.show_batch()


# ## Creating a Learner

# OK let's define our model and create a `Learner` from the model and the dataloaders. We also pass in our competition metric, which is Quadratic Cohen's Kappa. This is a good metric when studying inter-observer variability.

# In[ ]:


m = pretrainedmodels.se_resnext50_32x4d(pretrained='imagenet')
children = list(m.children())
head = nn.Sequential(nn.AdaptiveAvgPool2d(1), Flatten(), 
                                  nn.Linear(children[-1].in_features,200))
model = nn.Sequential(nn.Sequential(*children[:-2]), head)


# In[ ]:


learn = Learner(dls,model,splitter=default_split,loss_func = LabelSmoothingCrossEntropy(), opt_func=ranger, metrics=[accuracy,CohenKappa(weights='quadratic')])


# We have used the Label Smoothing Cross Entropy function, which is a regularization technique that will make our model more robust and generalize better.

# We can use the learning rate finder in order to find the best learning rate. We freeze the model for now.

# In[ ]:


learn.freeze()
learn.lr_find()


# From this, we can determine that maybe 3e-2 is a good learning rate. We could also do this once we unfreeze our model (as shown below).

# ## 5-fold CV

# Let's train a 5-fold CV ensemble. First, I write a function to train a model for a given fold.

# In[ ]:


def train_fold(fold,val_idx):
    panda_block = DataBlock(blocks=(ImageBlock, CategoryBlock),
                        splitter=IndexSplitter(val_idx),
                        get_x=ColReader('image_id',suff='.jpeg'),
                        get_y=ColReader('isup_grade'),
                        item_tfms=Resize(512),
                        batch_tfms=aug_transforms()
                       )
    dls = panda_block.dataloaders(train_df,bs=16)
    learn = Learner(dls,model,splitter=default_split,loss_func = LabelSmoothingCrossEntropy(), metrics=[CohenKappa(weights='quadratic')]).to_fp16()
    learn.freeze()
    learn.fit_flat_cos(5,3e-2,cbs=[SaveModelCallback(monitor='cohen_kappa_score')],pct_start=0.5)
    learn.save(f'stage-1-512-fold{fold}')
    learn = learn.load(f'stage-1-512-fold{fold}')
    learn.unfreeze()
    learn.fit_flat_cos(5,slice(1e-6,1e-3),cbs=[SaveModelCallback(monitor='cohen_kappa_score')],pct_start=0.5)
    learn.save(f'stage-2-512-fold{fold}')
    learn.export(f'fold{fold}.pkl')
    return learn.validate()[1]


# Let's set up a CV:

# In[ ]:


from sklearn.model_selection import StratifiedKFold
splits = StratifiedKFold(n_splits=5, random_state=SEED, shuffle=True)
scores = []
for fold, (trn_idx, valid_idx) in enumerate(splits.split(train_df,train_df.isup_grade)):
    score = train_fold(fold, valid_idx)
    scores.append(score)


# In[ ]:


print(f'5-fold CV score: {np.mean(scores)}')


# # Inference
# 
# This is a synchronous code-only competition. This means we submit inference kernels that run on the test set and generate predictions. In this case, the training kernel is also the inference kernel, but you could also separate them.
# 
# This competition presents a unique challenge in that there is no public test data available to run on. The test data is just made available during submission of the kernel. So be careful (I messed up 4 times before getting this to work) and make sure your kernel at least works on the train set and then use an if-statement (see below) to perform inference only when the test images are available.
# 
# In my kernel, I resize all the test images and save them, then perform inference on that.

# In[ ]:


os.mkdir('resized-test')


# In[ ]:


test_df = pd.read_csv('../input/prostate-cancer-grade-assessment/test.csv')


# In[ ]:


test_df.head(10)


# In[ ]:


sample_submission = pd.read_csv('../input/prostate-cancer-grade-assessment/sample_submission.csv')


# Here we define a function to resize the test images.

# In[ ]:


def resize_test_images():
    for i in test_df['image_id']:
        openslide_image = openslide.OpenSlide(str('../input/prostate-cancer-grade-assessment/test_images/'+i+'.tiff'))
        img = openslide_image.read_region(location=(0,0),level=2,size=(openslide_image.level_dimensions[2][0],openslide_image.level_dimensions[2][1]))
        Image.fromarray(np.array(img.resize((512,512)))[:,:,:3]).save('./resized-test/'+i+'.jpeg')
    test_df['image_id'] = './resized-test/' + test_df['image_id']


# Here we define an inference function that generates a test dataloader, then runs the model and gets the predictions. We use test-time augmentation (TTA), which is implemented in the fastai2 library.

# In[ ]:


def inference_fn(fold):
    test_dl = dls.test_dl(test_df)
    learn.load(f'stage-2-512-fold{fold}')
    preds, _ = learn.tta(dl=test_dl,beta=0)
    print(preds)
    test_preds = preds.argmax(-1)
    return test_preds


# We now write a function to perform inference for all the folds.

# In[ ]:


def inference_5folds():
    resize_test_images()
    predictions = torch.from_numpy(np.zeros((len(test_df))))
    for i in range(5):
        test_preds = inference_fn(i)
        predictions = predictions + test_preds
    
    predictions = torch.round(predictions/5)
    sample_submission.isup_grade = predictions
    sample_submission['isup_grade'] = sample_submission['isup_grade'].astype(int)


# This if-statement is necessary for proper submission of the code.

# In[ ]:


if os.path.exists('../input/prostate-cancer-grade-assessment/test_images'):
    print('inference!')
    inference_5folds()


# When we submit the kernel, the above code will run and the submission dataframe will be populated with our predictions. We just save our submission CSV:

# In[ ]:


sample_submission.to_csv('submission.csv', index=False)


# In[ ]:


sample_submission.head(10)


# Now, **WE ARE DONE**!

# If you enjoyed this kernel, please give it an upvote. Also check out the following resources below:
# 
# Datasets used in this kernel:
# - [512x512 resized dataset](https://www.kaggle.com/tanlikesmath/panda-challenge-512x512-resized-dataset) 
# 
# - [Cadene's pretrainedmodels](https://www.kaggle.com/rishabhiitbhu/pretrainedmodels) 
# 
# - [PyTorch SE-ResNext weights](https://www.kaggle.com/yasufuminakama/pytorch-se-resnext)
# 
# - [fastai2 wheels](https://www.kaggle.com/vijayabhaskar96/fastai2-wheels)
# 
# Other useful kernels/datasets I have:
# 
# - [256x256 resized dataset](https://www.kaggle.com/tanlikesmath/panda-challenge-256x256-resized-dataset)
# - [precursor kernel (fastai2 training baseline)](https://www.kaggle.com/tanlikesmath/fastai2-training-baseline)

# # References:
# 
# Wikipedia - Gleason grading system:
# https://en.wikipedia.org/wiki/Gleason_grading_system
# 
# Pathology Outlines - Grading (Gleason):
# http://www.pathologyoutlines.com/topic/prostategrading.html

# # Fin