#!/usr/bin/env python
# coding: utf-8

# # Importing Libraries

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from xgboost import XGBClassifier
from wordcloud import WordCloud
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
import string
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression,SGDClassifier, LinearRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from keras.layers import Dense, Conv1D, MaxPool1D, Flatten, Dropout, Embedding, LSTM
from keras.models import Sequential
from keras.utils import to_categorical


# In[ ]:


# loading data.
train_df = pd.read_csv('/kaggle/input/nlp-getting-started/train.csv')
test_df = pd.read_csv('/kaggle/input/nlp-getting-started/test.csv')
submission = pd.read_csv('/kaggle/input/nlp-getting-started/sample_submission.csv')


# In[ ]:


train_df.head()


# In[ ]:


test_df.head()


# In[ ]:


# filling nan values in the columns. 
train_df.keyword.fillna('', inplace=True)
train_df.location.fillna('', inplace=True)

test_df.keyword.fillna('', inplace=True)
test_df.location.fillna('', inplace=True)


# In[ ]:


train_df['text'] = train_df['text'] + ' ' + train_df['keyword'] + ' ' + train_df['location']
test_df['text'] = test_df['text'] + ' ' + test_df['keyword'] + ' ' + test_df['location']

del train_df['keyword']
del train_df['location']
del train_df['id']
del test_df['keyword']
del test_df['location']
del test_df['id']


# In[ ]:


train_df.head()


# In[ ]:


test_df.head()


# In[ ]:


sns.countplot(train_df.target)


# **We can see the target column is balanced.**

# # Text Cleaning

# In[ ]:


# As we already know there are lots of stopwords like 'a', 'our' which are no use to us while feature selection for our data.
# So we should remove them from our text
# creating list of stopwords.
stop = set(stopwords.words('english'))
punctuations = list(string.punctuation)
stop.update(punctuations)
print(stop)


# In[ ]:


# Functions to clean up the text like removing numbers and urls.
def remove_numbers(text):
    text = ''.join([i for i in text if not i.isdigit()])         
    return text

def remove_URL(text):
    url = re.compile(r'https?://\S+|www\.\S+')
    return url.sub(r'',text)

def remove_html(text):
    html=re.compile(r'<.*?>')
    return html.sub(r'',text)

def remove_emoji(text):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


# In[ ]:


train_df.text = train_df.text.apply(remove_numbers)
train_df.text = train_df.text.apply(remove_URL)
train_df.text = train_df.text.apply(remove_html)
train_df.text = train_df.text.apply(remove_emoji)
train_df.head()


# In[ ]:


test_df.text = test_df.text.apply(remove_numbers)
test_df.text = test_df.text.apply(remove_URL)
test_df.text = test_df.text.apply(remove_html)
test_df.text = test_df.text.apply(remove_emoji)
test_df.head()


# In[ ]:


# this function return the part of speech of a word.
def get_simple_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


# **Lemmatization is the process of grouping together the different inflected forms of a word so they can be analysed as a single item. Lemmatization is similar to stemming but it brings context to the words. So it links words with similar meaning to one word.**
# 
# **Text preprocessing includes both Stemming as well as Lemmatization.Actually, lemmatization is preferred over Stemming because lemmatization does morphological analysis of the words.**
# 
# **You guyz can read about lemmatization https://www.geeksforgeeks.org/python-lemmatization-with-nltk/ here.**

# In[ ]:


lemmatizer = WordNetLemmatizer()
def clean_text(text):
    clean_text = []
    for w in word_tokenize(text):
        if w.lower() not in stop:
            pos = pos_tag([w])
            new_w = lemmatizer.lemmatize(w, pos=get_simple_pos(pos[0][1]))
            clean_text.append(new_w)
    return " ".join(clean_text)


# In[ ]:


train_df.text = train_df.text.apply(clean_text)
test_df.text = test_df.text.apply(clean_text)


# # Data Visualisation

# In[ ]:


real = train_df.text[train_df.target[train_df.target==1].index]
fake = train_df.text[train_df.target[train_df.target==0].index]


# In[ ]:


plt.figure(figsize = (18,24)) # Text Reviews with real disaster
wordcloud = WordCloud(min_font_size = 3,  max_words = 2500 , width = 1200 , height = 800).generate(" ".join(real))
plt.imshow(wordcloud,interpolation = 'bilinear')


# In[ ]:


plt.figure(figsize = (18,24)) # Text Reviews with fake disaster
wordcloud = WordCloud(min_font_size = 3,  max_words = 2500 , width = 1200 , height = 800).generate(" ".join(fake))
plt.imshow(wordcloud,interpolation = 'bilinear')


# **As we can see in wordcloud some words like 'amp' is very frequent in our both data so it makes sense to ignore this word using attribute max_df (explained below)**

# # Splitting Data

# In[ ]:


# splitting our training data into train and validation just to check our model.
x_train_text, x_val_text, y_train, y_val = train_test_split(train_df.text, train_df.target, test_size=0.2, random_state=0)


# In[ ]:


#Min_df : It ignores terms that have a document frequency (presence in % of documents) strictly lower than the given threshold.
#For example, Min_df=0.66 requires that a term appear in 66% of the docuemnts for it to be considered part of the vocabulary.

#Max_df : When building the vocabulary, it ignores terms that have a document frequency strictly higher than the given threshold.
#This could be used to exclude terms that are too frequent and are unlikely to help predict the label.
tv=TfidfVectorizer(min_df=0,max_df=0.8,use_idf=True,ngram_range=(1,3))

#transformed train reviews
tv_train_reviews=tv.fit_transform(x_train_text)

#transformed validation reviews
tv_val_reviews=tv.transform(x_val_text)

#transformed test reviews
tv_test_reviews=tv.transform(test_df.text)

print('tfidf_train:',tv_train_reviews.shape)
print('tfidf_validation:',tv_val_reviews.shape)
print('tfidf_test:',tv_test_reviews.shape)


# # Models

# **1. Multinomial NaiveBayes Classifier**

# In[ ]:


# defining classifier
nb = MultinomialNB()

# fitting for tfidf vectorizer.
tfidf = nb.fit(tv_train_reviews, y_train)


# In[ ]:


# predicting for validation data
tfidf_val_predict = tfidf.predict(tv_val_reviews)
print('Tfidf Vectorizer score :',accuracy_score(y_val, tfidf_val_predict))


# In[ ]:


print(classification_report(y_val, tfidf_val_predict))


# In[ ]:


cm = confusion_matrix(y_val, tfidf_val_predict)
cm = pd.DataFrame(cm , index = [i for i in range(2)] , columns = [i for i in range(2)])
plt.figure(figsize = (8,6))
sns.heatmap(cm,cmap= "Blues", linecolor = 'black' , linewidth = 1 , annot = True, fmt='')


# **2. SVC Classifier**

# In[ ]:


svc = SVC()

# fitting for tfidf vectorizer.
tfidf = svc.fit(tv_train_reviews, y_train)


# In[ ]:


# predicting for validation data
tfidf_val_predict = tfidf.predict(tv_val_reviews)
print('Tfidf Vectorizer score :',accuracy_score(y_val, tfidf_val_predict))


# In[ ]:


print(classification_report(y_val, tfidf_val_predict))


# In[ ]:


cm = confusion_matrix(y_val, tfidf_val_predict)
cm = pd.DataFrame(cm , index = [i for i in range(2)] , columns = [i for i in range(2)])
plt.figure(figsize = (8,6))
sns.heatmap(cm,cmap= "Blues", linecolor = 'black' , linewidth = 1 , annot = True, fmt='')


# **3. XgBoostClassifier**

# In[ ]:


xgb = XGBClassifier()

# fitting for tfidf vectorizer.
tfidf = xgb.fit(tv_train_reviews, y_train)


# In[ ]:


# predicting for validation data
tfidf_val_predict = tfidf.predict(tv_val_reviews)
print('Tfidf Vectorizer score :',accuracy_score(y_val, tfidf_val_predict))


# In[ ]:


print(classification_report(y_val, tfidf_val_predict))


# In[ ]:


cm = confusion_matrix(y_val, tfidf_val_predict)
cm = pd.DataFrame(cm , index = [i for i in range(2)] , columns = [i for i in range(2)])
plt.figure(figsize = (8,6))
sns.heatmap(cm,cmap= "Blues", linecolor = 'black' , linewidth = 1 , annot = True, fmt='')


# **4. Random Forest Classifier**

# In[ ]:


rfc = RandomForestClassifier()

# fitting for tfidf vectorizer.
tfidf = rfc.fit(tv_train_reviews, y_train)


# In[ ]:


tfidf_val_predict = tfidf.predict(tv_val_reviews)
print('Tfidf Vectorizer score :',accuracy_score(y_val, tfidf_val_predict))


# In[ ]:


print(classification_report(y_val, tfidf_val_predict))


# In[ ]:


cm = confusion_matrix(y_val, tfidf_val_predict)
cm = pd.DataFrame(cm , index = [i for i in range(2)] , columns = [i for i in range(2)])
plt.figure(figsize = (8,6))
sns.heatmap(cm,cmap= "Blues", linecolor = 'black' , linewidth = 1 , annot = True, fmt='')


# **5. Creating Our Model**

# In[ ]:


model = Sequential()

model.add(Dense(units = 512 , activation = 'relu' , input_dim = tv_train_reviews.shape[1]))
model.add(Dense(units = 256 , activation = 'relu'))
model.add(Dense(units = 100 , activation = 'relu'))
model.add(Dense(units = 10 , activation = 'relu'))
model.add(Dense(units = 1 , activation = 'sigmoid'))

model.compile(optimizer = 'adam' , loss = 'binary_crossentropy' , metrics = ['accuracy'])

model.summary()


# In[ ]:


history = model.fit(tv_train_reviews, y_train, validation_data=(tv_val_reviews, y_val), batch_size=128, epochs=10)


# In[ ]:


# plotting accuracy and loss curves for train and validation data.
plt.figure(figsize=(10,12))
plt.subplot(221)
plt.title('Loss')
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')

plt.subplot(222)
plt.title('Accuracy')
plt.plot(history.history['accuracy'], label='train')
plt.plot(history.history['val_accuracy'], label='test')
plt.legend()
plt.show()


# In[ ]:


model_val_predict = model.predict_classes(tv_val_reviews)
cm = confusion_matrix(y_val, model_val_predict)
cm = pd.DataFrame(cm , index = [i for i in range(2)] , columns = [i for i in range(2)])
plt.figure(figsize = (8,6))
sns.heatmap(cm,cmap= "Blues", linecolor = 'black' , linewidth = 1 , annot = True, fmt='')


# # Predicting For Test Data

# In[ ]:


y_pred = model.predict_classes(tv_test_reviews)
submission.target = y_pred
submission.to_csv("submission.csv" , index = False)


# In[ ]:


y_pred = rfc.predict(tv_test_reviews)
submission.target = y_pred
submission.to_csv("submission.csv" , index = False)


# In[ ]:


y_pred = xgb.predict(tv_test_reviews)
submission.target = y_pred
submission.to_csv("submission.csv" , index = False)


# In[ ]:


y_pred = svc.predict(tv_test_reviews)
submission.target = y_pred
submission.to_csv("submission.csv" , index = False)


# In[ ]:


y_pred = nb.predict(tv_test_reviews)
submission.target = y_pred
submission.to_csv("submission.csv" , index = False)


# # If you face any kind of difficulty in code do comment down. Any kind of suggestions is much appreciated.
# # Don't forget to upvote. It's free :-)

# In[ ]:



