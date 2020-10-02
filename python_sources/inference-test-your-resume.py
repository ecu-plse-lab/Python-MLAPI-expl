#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import spacy
spacy.prefer_gpu()


# In[ ]:


model_path = '/kaggle/input/resume-named-entity-recognizer/model'


# In[ ]:


resume_txt = """RESUME  Abneet Wats      Vasai Virar, Mumbai 401208 abneetwats24@gmail.com +91 9373119739  To be a part of a challenging environment that enhances my skills, through which I would like to enrich the knowledge resource of the company and work towards its success.  EXPERIENCE  SKILLS  Openspace Services Pvt. Ltd., Mumbai-Python Developer JAN 2020 - PRESENT Working on Computer Vision and Natural Language Processing using Deep Neural Network.  INTERNSHIPS  Openspace Services Pvt. Ltd., Mumbai-Python Developer - Intern DEC 2019 - DEC 2020 Worked on rule based text extraction, tesseract, classification model using Convolution Neural Network.  Dongre Technoquip Pvt. Ltd., Mumbai  Software Engineer - PHP(Intern) JUN 2019 - NOV 2019 Worked designing and optimizing the database of CRM for Bisleri and the core product of the company.  EDUCATION  Government Engineering College, Patan  BE Computer Science JUN 2016 - JUN 2020 CGPA : 8.29/10  Kendriya Vidyalaya No 2, Surat  HSC APR 2015 - MAY 2016 Percentage : 76.8%.  Technologies : Python, MySQL  Theory : Neural Network, Computer Vision, Vector Algebra, Classification and regression ML algorithms  Library : OpenCV, Tensorflow2.0, Hugging Face NLP, Scikit-Learn, Keras  ACHIEVEMENTS  Grand Finalist of Smart India Hackathon 2017(SIH-17)  Grand Finalist of Smart City Rajkot Hackathon 2017  VOLUNTEERSHIP  National Service Scheme(2017-2019)  LANGUAGES  English, Hindi  WORK SAMPLE  abneetwats24 (Abneet Wats)  GitHub    \x0c  CERTIFICATIONS  Python for Data Science and AI by IBM (Online Coursera)  Machine Learning by Andrew Ng (Online Coursera Stanford University)  Kendriya Vidyalaya No 3, Gandhinagar  SSC APR 2013 - MAY 2014 CGPA : 9/10  PROJECTS  Resume Data Extraction  (OPENSPACE SERVICES) Information like Name, CollegeName, Skills are extracted from resumes of any format. Manual sequence tagging is done for training the neural network.  Technologies : Natural Language Processing, Named Entity Recognition, Tensorflow2.0, Python3   Algorithm : BiDirectional LSTM output layer  with Glove6B100d embedding layer  Invoice Entity Detection  (OPENSPACE SERVICES) Entity like Invoice No., Invoice Date, GST No. are to be detected from Invoice. Using custom training of pre-trained tensorflow ssd-mobilenet model  Technologies : Computer Vision, Tensorflow Object Detection from pretrained model, Python3  Algorithm : Object Detection in image then applying NLP to extract structured data using NER  Hindi International Phonetic Alphabet(IPA) Predictor  (OPENSPACE SERVICES)(POC) Predictive POC project which predicts  the Hindi IPA pronunciation of english words.  Technologies : NLP, Sequence2Sequence encoder decoder, Tensorflow2.0, Python3  Algorithm : Recurrent Neural Network  Health Report Data Retrieval  (OPENSPACE SERVICES) Details like test name, patient test value, reference  value are extracted from scanned and soft copies of the health report using rule based text extraction.  Technologies : Convolution Neural Network, Tesseract, Rule - based text extraction, Python3  \x0cAI-Letterpad  (BE MAJOR PROJECT) AI empowered blogging site whose functions includes: OCR of handwritten text for posting blogs.  Technologies : Tesseract(custom training), Laravel  House Price Prediction  (COURSE PROJECT) House Price Prediction implemented in octave  application using Linear Regression with Multiple Feature includes functions like: plotting data, feature normalization, cost computation, gradient descent, normal equation.  Technologies : Octave, Linear Regression"""


# In[ ]:


print("Loading from", model_path)
model = spacy.load(model_path)
resume = model(resume_txt)
print("Entities", [(ent.text, ent.label_) for ent in resume.ents])
# print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


# In[ ]:



