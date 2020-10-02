#!/usr/bin/env python
# coding: utf-8

# > This notebook was generated by Dr. Lida Ghahremanlou, NLP specialist and Data Scientist @ Microsoft UK

# # Round2 Group6 Diagnostics Methods for COVID-19
# 
# This notebook provides the steps and solution to address the task group5  (material studies) of round 2 for [COVID-19 Open Research Dataset Challenge (CORD-19)](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge).
# 
# ## Methodolgy 
# 
# The dataset of this challenge is the masive volumes of unstructed articles related to Covid-19 research. During round 1, many work have demonstrated various solutions for analysing and classifying the articles types and abstract contents. Most tasks of round 2 focus on **'Information Retreival'** from NLP approaches, meaning that the solution must either answer specific questions or retrieve relevant information for particular search quireis related to the Covid-19 documents.  
# 
# To address the group6 task,addressing diagnostics studies related to COVID-19, this notebook extracts the relevannt information from the bodies of the articles rather than their abstracts, because such information may not provided at that level, plus many articles lack abstracts.
# 
# 
# The steps to apply 'Information Extraction' are implemented as follows: 
# > 1. Load Data: modify the code sumbitted for one of the participants from round 1 to load the data from kaggle input. 
# > 1. Preprocess Data: split the artciles bodies into sentences, remove stop and custom words, tokenize each sentence.
# > 1. Word2Vec and Doc2Vec Cosin Similarity: apply both word2vec doc2vec between kaggle group6 search terms and sentences to generate word embeddings, calculate cosin similarity, rank the relevant sentences with relevant key search and threshold - the result of word2vec was slightly better. 
# > 1. BERT Pre-train Question Answering: Load the BERT fine-pre-train models, structure question-sentences pairs to extract the answers (run this part on a VM machines)
# > 1. Result: Repeat the above steps for 100 samples of articles for each diagnostics methods, join with orginal tables and generate csv files 
# > 1. Future Work: While word2vec generated fair word embeddings for this task, the word embeddings technigues can improve by using transformer language models. For the future work, the author plans to continue this research by applying other approaches for knowledge extraction such as [Microsoft Covid-19 Azure cognitive search](https://covid19search.azurewebsites.net/) and [Google REALM](https://kentonl.com/pub/gltpc.2020.pdf)
# * 
# 
# 
# 

# In[ ]:


#Import Packages
import sys
# Set the environment path
sys.path.append("../../")  
import os
from collections import Counter
import math
import numpy as np
import pandas as pd
import gensim
from gensim.models.doc2vec import LabeledSentence
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from scipy.spatial import distance
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import re
import nltk
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))


import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


print("System version: {}".format(sys.version))
print("Gensim version: {}".format(gensim.__version__))


# # Load Data
# 
# 
# 
# 

# In[ ]:


root_path = '/kaggle/input/CORD-19-research-challenge/'
metadata_path = f'{root_path}/metadata.csv'
meta_df = pd.read_csv(metadata_path, dtype={'pubmed_id': str,'Microsoft Academic Paper ID': str, 'doi': str})
meta_df.head()


# In[ ]:


import glob
all_json = glob.glob(f'{root_path}/**/*.json', recursive=True)
print('number of current articles : ',len(all_json))


# In[ ]:


import json
class FileReader:
    def __init__(self, file_path):
        with open(file_path) as file:
            content = json.load(file)
            #print(content)
            self.paper_id = content['paper_id']
            #self. = content['publish_time']
            self.abstract = []
            self.body_text = []
            # Abstract
            for entry in content['abstract']:
                self.abstract.append(entry['text'])
            # Body text
            for entry in content['body_text']:
                self.body_text.append(entry['text'])
            self.abstract = '\n'.join(self.abstract)
            self.body_text = '\n'.join(self.body_text)
    def __repr__(self):
        return f'{self.paper_id}: {self.abstract[:200]}... {self.body_text[:200]}...'
first_row = FileReader(all_json[0])
#print(first_row)


# In[ ]:


dict_ = {'paper_id': [], 'doi':[], 'abstract': [], 'body_text': [], 'title': [], 'journal': [], 'publish_time' : [] , 'cord_uid' : [] , 'who_covidence_id': [], 'url' : []  }
for idx, entry in enumerate(all_json):
    if idx>400:   #Process only 300 files 
        break
    if idx % (len(all_json) // 10) == 0:
        print(f'Processing index: {idx} of {len(all_json)}')    
    try:
        content = FileReader(entry)
    except Exception as e:
        continue  # invalid paper format, skip
    
    # get metadata information
    meta_data = meta_df.loc[meta_df['sha'] == content.paper_id]
    # no metadata, skip this paper
    if len(meta_data) == 0:
        continue
    
    dict_['abstract'].append(content.abstract)
    dict_['paper_id'].append(content.paper_id)
    dict_['body_text'].append(content.body_text)
        
    # get metadata information
    meta_data = meta_df.loc[meta_df['sha'] == content.paper_id]
    #print(meta_data['publish_time'])
    
    # add the title information, add breaks when needed
    try:
        title = get_breaks(meta_data['title'].values[0], 40)
        dict_['title'].append(title)
    # if title was not provided
    except Exception as e:
        dict_['title'].append(meta_data['title'].values[0])
    
    # add the journal information
    dict_['journal'].append(meta_data['journal'].values[0])
    
    # add doi
    dict_['doi'].append(meta_data['doi'].values[0])
    
    #print(meta_data['publish_time'])
    
    dict_['publish_time'].append(meta_data['publish_time'].values[0])
    dict_['cord_uid'].append(meta_data['cord_uid'].values[0])
    dict_['who_covidence_id'].append(meta_data['who_covidence_id'].values[0])
    dict_['url'].append(meta_data['url'].values[0])
    #dict_['s2_id'].append(meta_data['s2_id'].values[0])
    
df_covid = pd.DataFrame(dict_, columns=['paper_id', 'doi', 'abstract', 'body_text', 'title', 'journal', 'publish_time' , 'cord_uid', 'who_covidence_id', 'url' ])
df_covid.count()


# These settings are important for processing the articles for different methods. 
# 

# In[ ]:


number_of_articles  = 100 #sample files with doc2vec similarity threshold 
threshold = 0.4 #threshold for doc2vec cosin similarity 
start_kaggle_index= 0 #start index for particular kaggle query
end_kaggle_index = 5 #index for particular kaggle search query
subset_df_covid = df_covid.iloc[:number_of_articles,:] #only look at the 100 articles because the vec2wrod model consumes lots of memory.  
subset_df_covid = subset_df_covid[['paper_id','body_text','abstract']]
subset_df_covid.head()


# In[ ]:


print('Number of articles with no bodies',subset_df_covid['body_text'].isna().sum()) #no article with zero text


# # Preprocess Data

# In[ ]:


def apply_all_sent_token(doc):
    list_all_tokens = []
    all_sent = [nltk.word_tokenize(sents) for sents in doc]
    for one_sent in all_sent:
        filtered_tokens = []
        filtered_tokens =[words for words in one_sent if words not in stop_words]
        custom_removed_tokens = [words for words in filtered_tokens if words not in ['.','shown','fig.','figure','fig']]
        custom_removed_tokens = [words for words in custom_removed_tokens if len(words) > 2]
        list_all_tokens.append(custom_removed_tokens)
    return list_all_tokens


# In[ ]:


def split_sentences(article):
    import nltk.data
    import re
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    list_df = []
    marked_sentences = '***'.join(tokenizer.tokenize(article))
    marked_sentences = re.sub(r"(\[[0-9]*\])",'',marked_sentences) #remove the citations 
    marked_sentences = re.sub(r"(\([0-9]*\))",'',marked_sentences)
    list_df  = marked_sentences.split('***')
    return list_df


# In[ ]:


def preprocses_sentences(df):
    df_sent = df['body_text'].apply(lambda x: split_sentences(x)) #check abstract istead of abstract body-text
    df_lower = df_sent.apply(lambda doc: [sent.lower() if type(sent) == str else sent for sent in doc])
    df_clean = df_lower.apply(lambda doc: [re.sub(r"[^.a-z]",' ',sent) for sent in doc]) #remove punctation
    df_token = df_clean.apply(lambda doc:apply_all_sent_token(doc)) #tokenize all the sentences 
    preprocess_df=pd.concat([df,df_sent],axis = 1)
    preprocess_df=pd.concat([preprocess_df, df_token], axis=1)
    preprocess_df.columns=['paper_id','original_body', 'abstract','sentences','token_sentences']
    return preprocess_df


# In[ ]:


def prepare_kaggle_df():
    kaggle_df = pd.DataFrame()
   
     
    kaggle_group2 = [ 
                     'Detection Method in Diagnosing SARS-COV-2 with antibodies', 
                     'Sample in Diagnosing SARS-COV-2 with antibodie'
                     'Sample size in Diagnosing SARS-COV-2 with antibodies',       
                     'Measure in evidence in Diagnosing SARS-COV-2 with antibodies',
                     'Speed of assay in Diagnosing SARS-COV-2 with antibodies',
                     'FDA approval in Diagnosing SARS-COV-2 with antibodies'
        
        
                     'Detection Method in Diagnosing SARS-COV-2 with Nucleic-acid based technigues',
                     'Sample in Diagnosing SARS-COV-2 with Nucleic-acid based technigues'
                     'Sample szie in Diagnosing SARS-COV-2 with Nucleic-acid based technigues',  
                     'Measure of evidence in Diagnosing SARS-COV-2 with Nucleic-acid based technigues',
                     'Speed of assay in  Diagnosing SARS-COV-2 with Nucleic-acid based technigues',
                     'FDA approval in Diagnosing SARS-COV-2 with Nucleic-acid based technigues',
                    
        
        
                     'Detection Method in Development of a point-of-care test and rapid bed-side tests',
                     'Sample in Development of a point-of-care test and and rapid bed-side tests',
                     'Sample Size in Development of a point-of-care test and and rapid bed-side tests',
                     'Measure of evidence Development of a point-of-care test and rapid bed-side tests',
                     'Speed of assay in Development of a point-of-care test and rapid bed-side test',
                     'FDA approval in Development of a point-of-care and rapid bed-side test',
                                
                     
                    ]           
                     
                    
    kaggle_tokens=[nltk.word_tokenize(sents) for sents in kaggle_group2]
    kaggle_df['sentences']=[kaggle_group2]
    kaggle_df['token_sentences']=[kaggle_tokens]
    #print(kaggle_df.sentences[0])
    #print(len(kaggle_df.token_sentences.values))
    #print(len(kaggle_df.token_sentences.values.tolist()))
    return kaggle_df


# In[ ]:


def preprocess_data(df,number_of_artciles):
    preprocess_df=preprocses_sentences(df) 
    kaggle_df = prepare_kaggle_df()
    preprocess_df.head()
    kaggle_df.head()
    return preprocess_df,kaggle_df


# In[ ]:


def generate_article_df(one_article_df):
    all_articles_relevant_sentences_list = []
    article_df = pd.DataFrame()
    article_df['sentences'] = one_article_df['sentences']
    article_df['token_sentences'] =  one_article_df['token_sentences']
    return article_df


# In[ ]:


def transform_kaggle(kaggle_df, start_kaggle_index, end_kaggle_index):
    kaggle_list = [] 
    sent_list = []
    for index in range(len(kaggle_df.token_sentences.iloc[0])):
        kaggle_list.append(kaggle_df.token_sentences.apply(lambda x: x[index]))
    for index in range(len(kaggle_df.sentences.iloc[0])):
        sent_list.append(kaggle_df.sentences.apply(lambda x: x[index]))
    
    df = pd.DataFrame()    
    df = pd.concat(kaggle_list, axis=1,ignore_index=True)
    df2=pd.concat(sent_list,axis=1,ignore_index=True)
    df=df.transpose()
    df2=df2.transpose()
    kaggle_transformed_df = pd.concat([df2,df],axis=1)
    kaggle_transformed_df.columns=['sentences','token_sentences']
    kaggle_transformed_df = kaggle_transformed_df.loc[start_kaggle_index:end_kaggle_index]

    return kaggle_transformed_df


# # Doc2Vec

# In[ ]:


def prepare_doc2vec_tagged_documents(article_df, transformed_kaggle_df):
    article_sentences = article_df[['sentences']] 
    article_sentences_list = article_sentences.values.flatten().tolist()

 
    kaggle_sentences = transformed_kaggle_df[['sentences']]
    kaggle_sentences_list = kaggle_sentences.values.flatten().tolist()
   
    all_sentences_list = article_sentences_list + kaggle_sentences_list


    corpus = all_sentences_list
    len(corpus)

    # Produce dictionary of sentence to id
    sentence_id = {sent : i for i, sent in enumerate(corpus)} #
    
    # Assign id to sentences
    article_df['qid1'] = article_df['sentences'].apply(lambda row : sentence_id[row])
    transformed_kaggle_df['qid2'] = transformed_kaggle_df['sentences'].apply(lambda row : sentence_id[row])
    
     # Doc2vec requires data as Tagged Documents with the tokenized sentence and the sentence id
    article_df['labeled_tokens_article'] = article_df.apply(lambda x: TaggedDocument(x.token_sentences, str(x.qid1)), axis=1)
    transformed_kaggle_df['labeled_tokens_kaggle'] = transformed_kaggle_df.apply(lambda x: TaggedDocument(x.token_sentences, str(x.qid2)), axis=1)
    
    #Get all Tagged Documents
    labeled_article_sentences = article_df[['labeled_tokens_article']]  
    labeled_article_sentences_list = labeled_article_sentences.values.flatten().tolist()
    #print('num of one article sentences',len(all_sentences))
    labeled_kaggle_sentences = transformed_kaggle_df[['labeled_tokens_kaggle']]
    labeled_kaggle_sentences_list = labeled_kaggle_sentences.values.flatten().tolist()
    labeled_sentences= labeled_article_sentences_list + labeled_kaggle_sentences_list
    
    return labeled_sentences


# In[ ]:


def train_doc2vec_model(labeled_sentences):
    model = Doc2Vec(labeled_sentences, dm=1, min_count=1, window=10,negative=5, vector_size=100, epochs=30)
    
    # Train our model for 20 epochs
    for epoch in range(30):
        model.train(labeled_sentences, epochs=model.epochs, total_examples=model.corpus_count)
        
    return model


# In[ ]:


def doc2vec_cosine_similarity(article_df,transformed_kaggle_df,doc2vec_model, start_kaggle_index ,end_kaggle_index):
    for index in range(start_kaggle_index,end_kaggle_index):
        name = "task_" + str(index+1)
        kaggle_token = transformed_kaggle_df.loc[index]['token_sentences']
        article_df[name] = article_df.apply(lambda x: doc2vec_model.wv.n_similarity(x.token_sentences,kaggle_token) if len(x.token_sentences) != 0 else 0, axis = 1)
    return article_df


# In[ ]:


def doc2vec_per_article(one_article_df,transformed_kaggle_df,threshold, start_kaggle_index ,end_kaggle_index):
    article_df = generate_article_df(one_article_df)
    labeled_sentences = prepare_doc2vec_tagged_documents(article_df,transformed_kaggle_df)
    doc2vec_model = train_doc2vec_model(labeled_sentences)
    transformed_article_df=doc2vec_cosine_similarity(article_df,transformed_kaggle_df,doc2vec_model,start_kaggle_index ,end_kaggle_index)
    relevant_sentences_one_article= find_top_relevant_sentences(transformed_article_df,transformed_kaggle_df,threshold, start_kaggle_index ,end_kaggle_index) #put the threshold 
    return relevant_sentences_one_article


# In[ ]:


def word2vec_per_article(one_article_df,transformed_kaggle_df,threshold,start_kaggle_index ,end_kaggle_index):
    article_df = generate_article_df(one_article_df)
    sentence_embeddings_list,kaggle_embeddings_list= generate_word_embeddings(article_df,transformed_kaggle_df)
    transformed_article_df=generate_cosin_similarity(article_df,sentence_embeddings_list,kaggle_embeddings_list)
    relevant_sentences_one_article = find_top_relevant_sentences(transformed_article_df,transformed_kaggle_df,threshold, start_kaggle_index ,end_kaggle_index)
    return relevant_sentences_one_article
    


# In[ ]:


def find_top_relevant_sentences(article_df,kaggle_transformed_df,threshold,start_kaggle_index ,end_kaggle_index):
    relevant_sentences_df = pd.DataFrame()
    deduplicated_relevante_top_sentences = pd.DataFrame()
    final_relevant_sentences_list = []
    tmp_final=pd.DataFrame(columns={'sentences','score'})
    for index in range(start_kaggle_index,end_kaggle_index): 
        name = "task_" + str(index+1)
        tmp_df=article_df.sort_values(name, inplace = False, ascending=False).head(5) #sorting and select the top 5 sentences
        tmp2_df = tmp_df[['sentences',name]]
        tmp2_df = tmp2_df.rename(columns={name : "score"})
        tmp_final=tmp_final.append(tmp2_df, ignore_index=True) #concatinate all the sentences and score and scores
    relevant_sentences_df=tmp_final.sort_values('score',inplace = False, ascending = False) #sorting
    deduplicated_relevante_top_sentences = relevant_sentences_df.drop_duplicates('sentences',keep='first') #drop duplicates
    deduplicated_relevante_top_sentences['score'] = pd.to_numeric(deduplicated_relevante_top_sentences['score'],errors='coerce')
    final_relevante_sentences=deduplicated_relevante_top_sentences[deduplicated_relevante_top_sentences.score > threshold]
    return final_relevante_sentences 


# In[ ]:


def find_relevant_sentences_all_articles(preprocess_df,kaggle_df, threshold, start_kaggle_index,end_kaggle_index):
    all_relevant_sentences_list = []
    transformed_kaggle_df = transform_kaggle(kaggle_df,start_kaggle_index,end_kaggle_index)
    for index in range(len(preprocess_df)):
        one_article_relevant_sentences_list = []
        one_article_df=preprocess_df.iloc[index]
        #relevant_sentences_one_article=doc2vec_per_article(one_article_df,transformed_kaggle_df,threshold, start_kaggle_index ,end_kaggle_index)
        relevant_sentences_one_article = word2vec_per_article(one_article_df,transformed_kaggle_df,threshold,start_kaggle_index ,end_kaggle_index) #using word2vec instead of doc2vec
        for i in range(len(relevant_sentences_one_article)):
            one_article_relevant_sentences_list.append(relevant_sentences_one_article.iloc[i]['sentences'])
        all_relevant_sentences_list.append(one_article_relevant_sentences_list)
    preprocess_df['extracted_relevant_sentences_doc2word_group5'] = all_relevant_sentences_list
    return preprocess_df


# # Word2Vec

# In[ ]:


from gensim.models.keyedvectors import KeyedVectors
import word2vec
word2vec_model = KeyedVectors.load_word2vec_format('/kaggle/input/word2vecgooglenewsmodel/GoogleNews-vectors-negative300.bin', binary =True)


# In[ ]:


def generate_word_embeddings(transformed_article_df,transformed_kaggle_df):   
    all_sentences = transformed_article_df[['token_sentences']]
    all_sentences_list = all_sentences.values.flatten().tolist()
    #print(len(all_sentences_list))
    kaggle_sentences = transformed_kaggle_df[['token_sentences']]
    #print(kaggle_sentences)
    kaggle_sentenes_list = kaggle_sentences.values.flatten().tolist()
    #print(len(kaggle_sentenes_list))
    all_sentences = all_sentences_list + kaggle_sentenes_list
    #print(len(all_sentences))
    document_frequency_dict, num_documnets = get_document_frequency(all_sentences)
    sentence_embeddings_list = average_word_embedding_cosine_similarity(transformed_article_df, word2vec_model,document_frequency_dict,num_documnets)
    kaggle_embeddings_list = average_word_embedding_cosine_similarity(transformed_kaggle_df, word2vec_model,document_frequency_dict,num_documnets)
    #print('sentence_embeddings ' ,len(sentence_embeddings_list))
    #print(len(kaggle_embeddings_list))
    return sentence_embeddings_list,kaggle_embeddings_list


# In[ ]:


def generate_cosin_similarity(transformed_article_df,sentence_embeddings_list,kaggle_embeddings_list):
    for index in range(len(kaggle_embeddings_list)): #len(kaggle_embeddings_list)
        cosine_similarity = []
        name = "task_" + str(index+1)
        for index2 in range(len(sentence_embeddings_list)):
            one_sentence_embeddings = sentence_embeddings_list[index2]
            kaggle_embeddings = kaggle_embeddings_list[index]
            if sum(one_sentence_embeddings) != 0 and sum(kaggle_embeddings)!= 0:
                #print(calculate_modified_cosine_similarity(one_sentence_embeddings,kaggle_embeddings))
                cosine_similarity.append(calculate_cosine_similarity(one_sentence_embeddings,kaggle_embeddings))
            else: 
                #print(0)
                cosine_similarity.append(0)
        #print(len(cosine_similarity))
        transformed_article_df[name]= cosine_similarity 
    #cosine_df[name]=pd.Series(cosine_similarity) 
    return transformed_article_df


# In[ ]:


def get_document_frequency(all_sentences_list):
    """Iterate through all sentences in dataframe and create a dictionary 
    mapping tokens to the number of sentences in our corpus they appear in
    
    Args:
        df (pandas dataframe): dataframe of sentence pairs with their similarity scores
        
    Returns:
        document_frequency_dict (dictionary): mapping from tokens to number of sentences they appear in
        n (int): number of sentences in the corpus
    """
    document_frequency_dict = {}
    all_sentences = []
    all_sentences = all_sentences_list     
    n = len(all_sentences)

    for s in all_sentences:
        for token in set(s):
            document_frequency_dict[token] = document_frequency_dict.get(token, 0) + 1

    return document_frequency_dict, n


# In[ ]:


def average_word_embedding_cosine_similarity(df, embedding_model, document_frequencies,num_documnets, rm_stopwords=False):
    """Calculate the cosine similarity between TF-IDF weighted averaged embeddings
    
    Args:
        df (pandas dataframe): dataframe as provided by the nlp_utils
        embedding_model: word embedding model
        rm_stopwords (bool): whether to remove stop words (True) or not (False)
    
    Returns:
        list: predicted values for sentence similarity of test set examples
    """
   
    sentence_embedding = df.apply(lambda x: average_sentence_embedding(x.token_sentences, embedding_model,document_frequencies, num_documnets), axis=1)
     
    return sentence_embedding.tolist()


# In[ ]:


def calculate_cosine_similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embedding vectors
    
    Args:
        embedding1 (list): embedding for the first sentence
        embedding2 (list): embedding for the second sentence
    
    Returns:
        list: cosine similarity value between the two embeddings
    """
    # distance.cosine calculates cosine DISTANCE, so we need to
    # return 1 - distance to get cosine similarity
    cosine_similarity = 1 - distance.cosine(embedding1, embedding2)
    return cosine_similarity


# In[ ]:


def average_sentence_embedding(tokens, embedding_model,document_frequencies, num_documents):
    """Calculate TF-IDF weighted average embedding for a sentence
    
    Args:
        tokens (list): list of tokens in a sentence
        embedding_model: model to use for word embedding (word2vec, glove, fastText, etc.)
    
    Returns:
        list: vector representing the sentence
    """
    # Throw away tokens that are not in the embedding model
    tokens = [i for i in tokens if i in embedding_model]

    if len(tokens) == 0:
        return []

    # We will weight by TF-IDF. The TF part is calculated by:
    # (# of times term appears / total terms in sentence)
    count = Counter(tokens)
    token_list = list(count)
    term_frequency = [count[i] / len(tokens) for i in token_list]

    #print(num_documents)
    # Now for the IDF part: LOG(# documents / # documents with term in it)
    inv_doc_frequency = [
        math.log(num_documents / (document_frequencies.get(i, 0) + 1)) for i in count
    ]

    # Put the TF-IDF together and produce the weighted average of vector embeddings
    word_embeddings = [embedding_model[token] for token in token_list]
    weights = [term_frequency[i] * inv_doc_frequency[i] for i in range(len(token_list))]
    return list(np.average(word_embeddings, weights=weights, axis=0))


# ## Run Methods

# In[ ]:


preprocess_df, kaggle_df = preprocess_data(subset_df_covid,number_of_articles)
preprocess_df.head()


# In[ ]:


final_preprocess_df = find_relevant_sentences_all_articles(preprocess_df,kaggle_df,threshold,start_kaggle_index ,end_kaggle_index)
final_preprocess_df.head()


# In[ ]:


#save the file to be processed in a VM machine for importing transformers
#final_preprocess_df.to_csv('./method3_word2vec.csv',index= False) #method1 and method2 are already saved


# # BERT Pre-trained Question-Answer Model
# 

# # Note: 
# Transformers cannot be installed in this notebook due to some weired behaviour of the environment. I saved the current result into a csv file and ran the BERT Question-Answer function at the Linux VM with the following settings: 
# 
# 

# In[ ]:


#!pip install transformers


# In[ ]:


#def BERT_Qquestion_Answer(question,text):
    
#    from transformers import BertTokenizer, BertForQuestionAnswering
#    import torch
#    tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
#    model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    
#    input_text = "[CLS] " + question + " [SEP] " + text + " [SEP]"
#    import re
#    #print(input_text)
#    encoding = tokenizer.encode_plus(
#                    input_text,                      # Sentence to encode.
#                    max_length = 512,           # Pad & truncate all sentences.
#                    pad_to_max_length = True,
#                    return_attention_mask = True,   # Construct attn. masks.
    
#    )

#    input_ids, token_type_ids = encoding["input_ids"], encoding["token_type_ids"]
#    start_scores, end_scores = model(torch.tensor([input_ids]), token_type_ids=torch.tensor([token_type_ids]))
 
#    # Find the tokens with the highest `start` and `end` scores.
#    answer_start = torch.argmax(start_scores)
#    answer_end = torch.argmax(end_scores)
    

    # Get the string versions of the input tokens.
#    tokens = tokenizer.convert_ids_to_tokens(input_ids)

    # Start with the first token.
 #   answer = tokens[answer_start]

    # Select the remaining answer tokens and join them with whitespace.
 #   for i in range(answer_start + 1, answer_end + 1):
        
        # If it's a subword token, then recombine it with the previous token.
#        if tokens[i][0:2] == '##':
 #           answer += tokens[i][2:]
        
        # Otherwise, add a space then the token.
  #      else:
   #         answer += ' ' + tokens[i]

        
   # return answer


# In[ ]:


#new_df  = pd.read_csv('./method1_BERT_result.csv') #load the data from files
#new_df.count() #400 files for training
#sentence_list = preprocess_df.extracted_relevant_sentences_doc2word_group5.apply(lambda x:x)
#question_list = ['what is the study type?','what detection method is used?','what is the sample size?','what sample is obtained?',
#                 'what are the measures of evidence?','what is the speed of assay?','Is it FDA approval?']

#all_answer_list = []
#for qindex in range(len(question_list)):
#    answer_list = list()
#    for index in range(len(sentence_list)):
#        answer=BERT_Qquestion_Answer(question_list[qindex],sentence_list[index])
#        #print('answer',answer)
#        answer_list.append(answer)
#    all_answer_list.append(answer_list)


# In[ ]:


#new_df['study_type'] = all_answer_list[0]
#new_df['method'] = all_answer_list[1]
#new_df['sample_size'] = all_answer_list[2]
#new_df['Sample_obtained'] = all_answer_list[3]
#new_df['measure'] = all_answer_list[4]
#new_df['assay'] = all_answer_list[5]
#new_df['FDA'] = all_answer_list[6]


# In[ ]:


#new_df.to_csv('method3_BERT_result.csv') #save to files to be loaded again for generating final results - this part was done in a Linux VM environment


# # Results

# In[ ]:


df_target = pd.DataFrame(columns = ['Publication Date','Study', 'Study Link', 'Journal','Study Type', ' Detected Method', 'Sample Obtained','Sample Size','Measure of Evidence','Speed of Assay','FDA Approval','DOI CORD_UID'])


# Load result csv file and join with original dataframe and generate the target files

# In[ ]:


pd.read_csv('../input/bertfinalqaresults/method1_BERT_result.csv')


# In[ ]:





# In[ ]:


df_method1_BERT_result = pd.read_csv('../input/bertfinalqaresults/method1_BERT_result.csv')
df_method1 = df_covid.loc[:100,:]
df_method1=df_method1.merge(df_method1_BERT_result, on = 'paper_id', how='inner')
df_target1=pd.concat([df_method1.publish_time,df_method1.title,df_method1.url,df_method1.journal,df_method1.study_type,df_method1.method,df_method1.sample_obtained,df_method1.sample_size,df_method1.measure,df_method1.assay,df_method1.FDA,df_method1.doi],axis=1)
df_target1 = df_target1.replace(np.nan,'')
df_target1.columns = ['Publication Date','Study', 'Study Link', 'Journal','Study Type', ' Detected Method', 'Sample Obtained','Sample Size','Measure of Evidence','Speed of Assay','FDA Approval','DOI CORD_UID']
df_target1


# In[ ]:


df_target1.to_csv('./Group6_Diagnostics_target_table1.csv')


# ## Target_Table2: Diagnosing SARS-COV-2 with Nucleic-acid based tech

# In[ ]:


df_method2_BERT_result = pd.read_csv('/kaggle/input/bertfinalqaresults/method2_BERT_result.csv')
df_method2 = df_covid.loc[101:200,:]
df_method2=df_method2.merge(df_method2_BERT_result, on = 'paper_id', how='inner')
df_target2=pd.concat([df_method2.publish_time,df_method2.title,df_method2.url,df_method2.journal,df_method2.study_type,df_method2.method,df_method2.sample_obtained,df_method2.sample_size,df_method2.measure,df_method2.assay,df_method2.FDA,df_method2.doi],axis=1)
df_target2 = df_target2.replace(np.nan,'')
df_target2.columns = ['Publication Date','Study', 'Study Link', 'Journal','Study Type', ' Detected Method', 'Sample Obtained','Sample Size','Measure of Evidence','Speed of Assay','FDA Approval','DOI CORD_UID']
df_target2


# In[ ]:


df_target2 = pd.read_csv('/kaggle/input/expectedoutput/Group6_Diagnostics_target_table2.csv', index_col=0)  #this file was generated by my notebook
df_target2


# In[ ]:


df_target2.to_csv('./Group6_Diagnostics_target_table2.csv') 


# ## Target_Table3: Diagnosing SARS-COV-2 with antibodies

# In[ ]:


df_method3_BERT_result = pd.read_csv('/kaggle/input/bertfinalqaresults/method3_BERT_result.csv', index_col=0)
df_method3 = df_covid.loc[200:300,:]
df_method3=df_method3.merge(df_method3_BERT_result, on = 'paper_id', how='inner')
df_target3=pd.concat([df_method3.publish_time,df_method3.title,df_method3.url,df_method3.journal,df_method3.study_type,df_method3.method,df_method3.Sample_obtained,df_method3.sample_size,df_method3.measure,df_method3.assay,df_method3.FDA,df_method3.doi],axis=1)
df_target3= df_target3.replace(np.nan,'')
df_target3.columns = ['Publication Date','Study', 'Study Link', 'Journal','Study Type', ' Detected Method', 'Sample Obtained','Sample Size','Measure of Evidence','Speed of Assay','FDA Approval','DOI CORD_UID']
df_target3


# In[ ]:


df_target3 = pd.read_csv('/kaggle/input/expectedoutput/Group6_Diagnostics_target_table3.csv', index_col=0) #this file was generated by my notebook
df_target3


# In[ ]:


df_target3.to_csv('./Group6_Diagnostics_target_table3.csv')


# **Submission Correction:** My notebook generated the output files when it is private. I don't know why the outcomes are not shown when the notebook becomes public. I therefore saved the outcome in my local machine and loaded back to the kaggle notebook.   