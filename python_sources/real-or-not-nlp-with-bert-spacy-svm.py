#!/usr/bin/env python
# coding: utf-8

# >#  Work flow of this notebook
# * Spacy and SVM
# * Bert

# # 1. Spacy and SVM

# In[ ]:


import numpy as np 
import pandas as pd

import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from spacy import displacy


# In[ ]:


nlp=spacy.load("en_core_web_sm")


# In[ ]:


train=pd.read_csv('/kaggle/input/nlp-getting-started/train.csv')
test=pd.read_csv('/kaggle/input/nlp-getting-started/test.csv')


# In[ ]:


train.head()


# In[ ]:


from spacy.lang.en.stop_words import STOP_WORDS
stopwords = list(STOP_WORDS)
import string
punct=string.punctuation

def text_data_cleaning(sentence):
    doc = nlp(sentence)
    
    tokens = []
    for token in doc:
        if token.lemma_ != "-PRON-":
            temp = token.lemma_.lower().strip()
        else:
            temp = token.lower_
        tokens.append(temp)
    
    cleaned_tokens = []
    for token in tokens:
        if token not in stopwords and token not in punct:
            cleaned_tokens.append(token)
    return cleaned_tokens


# In[ ]:


from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# In[ ]:


tfidf = TfidfVectorizer(tokenizer = text_data_cleaning)
classifier = LinearSVC()


# In[ ]:


x = train['text']
y = train['target']


# In[ ]:


X_train, X_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 42)


# In[ ]:


clf = Pipeline([('tfidf', tfidf), ('clf', classifier)])


# In[ ]:


clf.fit(X_train,y_train)


# In[ ]:


y_pred = clf.predict(X_test)


# In[ ]:


print(classification_report(y_test, y_pred))


# In[ ]:


y_pred=clf.predict(test['text'])


# In[ ]:


sub_file=pd.DataFrame({'id':test['id'],'target':y_pred.round().astype(int)})


# In[ ]:


# sub_file.to_csv('submission.csv',index=False)


# # 2.BERT

# In[ ]:


get_ipython().system('wget --quiet https://raw.githubusercontent.com/tensorflow/models/master/official/nlp/bert/tokenization.py')


# In[ ]:


import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import ModelCheckpoint
import tensorflow_hub as hub

import tokenization


# In[ ]:


def bert_encode(texts, tokenizer, max_len=512):
    all_tokens = []
    all_masks = []
    all_segments = []
    
    for text in texts:
        text = tokenizer.tokenize(text)
            
        text = text[:max_len-2]
        input_sequence = ["[CLS]"] + text + ["[SEP]"]
        pad_len = max_len - len(input_sequence)
        
        tokens = tokenizer.convert_tokens_to_ids(input_sequence)
        tokens += [0] * pad_len
        pad_masks = [1] * len(input_sequence) + [0] * pad_len
        segment_ids = [0] * max_len
        
        all_tokens.append(tokens)
        all_masks.append(pad_masks)
        all_segments.append(segment_ids)
    
    return np.array(all_tokens), np.array(all_masks), np.array(all_segments)


# In[ ]:


def build_model(bert_layer, max_len=512):
    input_word_ids = Input(shape=(max_len,), dtype=tf.int32, name="input_word_ids")
    input_mask = Input(shape=(max_len,), dtype=tf.int32, name="input_mask")
    segment_ids = Input(shape=(max_len,), dtype=tf.int32, name="segment_ids")

    _, sequence_output = bert_layer([input_word_ids, input_mask, segment_ids])
    clf_output = sequence_output[:, 0, :]
    out = Dense(1, activation='sigmoid')(clf_output)
    
    model = Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=out)
    model.compile(Adam(lr=2e-6), loss='binary_crossentropy', metrics=['accuracy'])
    
    return model


# In[ ]:


get_ipython().run_cell_magic('time', '', 'module_url = "https://tfhub.dev/tensorflow/bert_en_uncased_L-24_H-1024_A-16/1"\nbert_layer = hub.KerasLayer(module_url, trainable=True)')


# In[ ]:


vocab_file = bert_layer.resolved_object.vocab_file.asset_path.numpy()
do_lower_case = bert_layer.resolved_object.do_lower_case.numpy()
tokenizer = tokenization.FullTokenizer(vocab_file, do_lower_case)


# In[ ]:


train_input = bert_encode(train.text.values, tokenizer, max_len=160)
test_input = bert_encode(test.text.values, tokenizer, max_len=160)
train_labels = train.target.values


# In[ ]:


model = build_model(bert_layer, max_len=160)
model.summary()


# In[ ]:


train_history = model.fit(
    train_input, train_labels,
    validation_split=0.2,
    epochs=3,
    batch_size=16
)


# In[ ]:


test_pred = model.predict(test_input)


# In[ ]:


submission=pd.DataFrame()
submission['id']=test['id']
submission['target'] = test_pred.round().astype(int)
submission.to_csv('submission.csv', index=False)


# In[ ]:


submission.head()


# In[ ]:



