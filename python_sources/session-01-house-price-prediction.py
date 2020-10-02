#!/usr/bin/env python
# coding: utf-8

# STEPS
# 1. LOAD THE DATA
# 2. CREATE THE MODEL
# 3. TRAIN THE MODEL ON THE DATA
# 4. PREDICT WITH SOME NEW DATA
# 5. EVALUATE THE RESULTS(TRAIN TEST SPLIT)
# 6. SAVE THE MODEL 
# 7. EXPORT MODEL TO AN APPLICATION

# **HOUSE PRICE PREDICTION SYSTEM USING MACHINE LEARNING**

# ![house](data:image/jpeg;base64,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)

# **Linear Regression - Finding a linear relationship between features and target variables. PREDICT HOUSE PRICES- House value is simply more than location and square footage.**

# * Flask==1.1.1
# * gunicorn==19.9.0
# * itsdangerous==1.1.0
# * Jinja2==2.10.1
# * MarkupSafe==1.1.1
# * Werkzeug==0.15.5
# * numpy>=1.9.2
# * scipy>=0.15.1
# * scikit-learn>=0.18
# * matplotlib>=1.4.3
# * pandas>=0.19
#  

# In[ ]:


# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle

dataset = pd.read_csv('../input/housepricedata/train_hp.csv')

dataset = dataset.dropna()


X = dataset.iloc[:, : 29]

y = dataset.iloc[:, -1]


#Splitting Training and Test Set
#Since we have a very small dataset, we will train our model with all availabe data.

from sklearn.linear_model import LinearRegression
regressor = LinearRegression()

#Fitting model with trainig data
regressor.fit(X, y)

# Saving model to disk
pickle.dump(regressor, open('model.pkl','wb'))

# Loading model to compare the results
model = pickle.load(open('model.pkl','rb'))
print(model.predict([[60,65,8450,7,5,2003,2003,706,0,150,856,856,854,1710,1,0,2,1,3,1,8,2003,2,548,0,0,0,2,2008]]))


# In[ ]:


import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = [int(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    prediction = model.predict(final_features)

    output = round(prediction[0], 2)

    return render_template('index.html', prediction_text='Predicted House Price $ {}'.format(output))

@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)


# In[ ]:





# In[ ]:





# In[ ]:



