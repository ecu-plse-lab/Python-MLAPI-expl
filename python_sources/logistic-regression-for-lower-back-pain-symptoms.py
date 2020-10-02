#!/usr/bin/env python
# coding: utf-8

# # **Logistic Regression with Lower Back Pain Symptoms**
# 
# In this kernel, we are going to apply logistic regression algorithm using mathematical formulas and also using sklearn library and see the differences.
# 
# Logistic Regression algorithm is used to predict if the result is Yes or No, A or B, Cat or Dog etc. Our data set includes back pain symptoms that are classified as Abnormal or Normal and suitable for applying Logistic Regression.
# 
# First we start with importing necessary libraries and load our data set.

# In[ ]:


#Import necessary libraries
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt #for visiulazitions

#Load data set
data = pd.read_csv("../input/Dataset_spine.csv")


# **Exploratory Data Analysis**
# 
# It is very important to explore our data set before started working on it. In this section we look at some statistical values of our data set.
# 

# In[ ]:


data.info() #gives information about column types and NaN values


# There are 14 columns and 310 rows data. All columns have 310 rows that means there is not any NaN values so we don't have to handle missing values. There are 2 object type columns, and the rest of them are all float type. In order to work on data, all columns have to be in integer or float type, so we need to convert them or delete them if not needed.
# 
# Let's look at the data by getting the first 10 rows:

# In[ ]:


data.head(10) #gets first 10 row of the data


# Class_att column gives if the  pain is Abnormal or Normal, we are going to use this column but we need to store the values as integer, not text. Unnamed: 13 column seems unnecessary and is not important for our statistical model. It only contains the technical names of columns. So we may  store only useful rows and then delete the column. 

# In[ ]:


#Store attribute names which are written in "Unnamed: 13" column, then delete the column
attribute_names = data.iloc[5:17]["Unnamed: 13"]
data.drop(["Unnamed: 13"],axis=1,inplace=True)


# Class_att column includes only two class names; Normal and Abnormal. Let's convert it as 1 and 0.

# In[ ]:


#Convert two class names to 0 and 1
data.Class_att = [1 if each == "Abnormal" else 0 for each in data.Class_att]


# In[ ]:


data.describe() #gives some statistical values about data set, such as max,min,mean,median etc.


# **Normalization**
# 
# The statistical table shows us that there are some columns including big values such as Col6 and some columns including small values such as Col7. If we use the original values in dataset, then we probably ignore the changes in Col7. But Col7 column may be really important, we don't know. So we need to make the ranges between min and max values of each column equally. This can be done by fitting all values between 0 and 1. This is called Normalization.
# 
# **Assigning x and y Values**
# 
# We need to split our data into two dimension as x and y values. y value is our class name, which gives if the row is Abnormal or Normal. So, we assign Class_att column as y values then drop the column from data set. The rest of the data ; all Col1, Col2..., Col12 columns will be our x value.
# Add .values function to convert both x and y values to numpy arrays.

# In[ ]:


#assign Class_att column as y attribute
y = data.Class_att.values

#drop Class_att column, remain only numerical columns
new_data = data.drop(["Class_att"],axis=1)

#Normalize values to fit between 0 and 1. 
x = (new_data-np.min(new_data))/(np.max(new_data)-np.min(new_data)).values


# **Split Data into Train and Test**
# 
# It is important to split the data set into train and test in order to calculate if our algorithm is successfull or not. We will apply our algorithm to train data, then we predict the results of test data and compare the prediction with actual results. Generally train and test data is splitted as (%70 train and %30 test) or (%80train and %20test). Splitting can be done easily with sklearn library like below.  I preferred to split the data as 80-20, so test_size parameter would be 0.2. 
# 
# Train_test_split function splits the data randomly according to size everytime, if you don't give a random_state parameter. This causes to get different results everytime you run the all algorithm. random_state = 42 parameter is used to stabilize the randomization. That means the function splits the data randomly but according to a rule and every time you run the algorithm, you will get same train and test data.

# In[ ]:


#Split data into Train and Test 
from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2,random_state =42)


# After this point, I will continue with two ways. One is the long way with applying mathematical formulas, and the other is the short way with using sklearn library. The code above is in common for both two solutions.
# 
# Before starting the solutions, transpose all x_train, x_test, y_train, y_test matrices to make easier matrix multiplication in next steps.

# In[ ]:


#transpose matrices
x_train = x_train.T
y_train = y_train.T
x_test = x_test.T
y_test = y_test.T


# **Solution 1 : Mathematical Formulas**
# 
# The formula of logistic regression is like below. 
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=18Abf4M3pabdE3BAjXinnVhLqcAfWGvQ0' 
#          style="width: 200px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 
# According to formula; x value would be our x_train matrix. w means weights, and b means bias. But we haven't known what is w and b values, yet. We need to find weight values for each Col1, Col2,...,Col12 and a single bias value. 
# For this dataset, our w matrix will have 12 values. Then we will multiply x_train matrix with transpose of w matrix and then add bias value. The result would have no meaning at this point, so we apply sigmoid function to find a y_head value. Sigmoid function gives the result a probabilistic value between 0 and 1. At first try, the result would be so wrong because we don't know what should be optimal w and b values.  
# Then, according to y_head and y_train values, we will calculate the loss and cost of this iteration. At first iteration, cost would be so high because the result is wrong. We need to minimize the cost in order to find the optimal w and b values.
# 
# Now, let's start one by one:
# 
# For first iteration, we need to assign some values to w and b. Generally, initial values are given as 0.0 for b and 0.01 for w. w must be a matrix that has a size of 12(column number of x_train) for our data set. Let's write a function get the dimension as parameter, and fill all values as 0.01 for w. 

# In[ ]:


#parameter initialize and sigmoid function
def initialize_weights_and_bias(dimension):
    
    w = np.full((dimension,1),0.01) #first initialize w values to 0.01
    b = 0.0 #first initialize bias value to 0.0
    return w,b


# Shape of w matrix would be (12,1) and shape of our x_train matrix is (12,248). In order to make matrix multiplication, second value of first matrix and first value of second matrix must be same. If we transpose w, its shape would be (1,12) so that we can multiply it with (12,248) sized matrix and get a (1,248) sized matrix as a result.
# 
# Then, we need to apply sigmoid. Formula of sigmoid function is like below;
# 
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=1FeoFow8XsC2Ex2O2devehGeELewPmFQS' 
#          style="width: 200px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 

# In[ ]:


#sigmoid function fits the z value between 0 and 1
def sigmoid(z):
    
    y_head = 1/(1+ np.exp(-z))
    return y_head


# Now we are able to calculate y_head values according to logistic regression formula. Then we need to calculate the loss and cost of our iteration.
# 
# Formulas of loss and cost functions are like below.
# 
# In loss formula, y would be our y_train matrix and y_head would be the result of logistic regression formula that we find.
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=1eTEGZtUR2hA40ynqjqGzXKZMeklDvEeE' 
#          style="width: 400px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 
# In cost formula, we sum total loss that we find according the formula above, then we divide the result to sample size, which is 248 for our data set.
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=1b-JNQntWBivulojfCX26ROV3rcfozcNB' 
#          style="width: 200px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 
# All this process; finding y_head and then calculating loss and cost is called forward propagation. Now it is time to go backward and find new w and b values that gives a lower cost. This is called backpropagation. With doing lots of forward-backward propogations, we try to find the minimum cost and w and b values that gives minimum cost.
# 
# In order to go backward, Gradient Descent formula can be used.
# 
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=1zOLAAnYuc9XWG9DpeA1njTtPBkIxrA5S' 
#          style="width: 400px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 
# 
# According to graph above, we started with an initial w value. This w value has a slope over the curve bigger than 0. We need to change w and b values step by step and try to find minimum cost which is shown as red circle. How to undertstand that we find minimum cost? At minimum cost, if we draw a line like red line shown on the graph, the slope between red line and curve will be 0 because red line is parallel to x-axis. This means that we need to continue iterations until we find slope is 0 or nearly 0. This technique is called Gradient Descent.
# 
# At every iteration, we go backward, update w and b, then calculate loss and cost. Update function of both w and b are like below. There is also another variable named as alpha in the equation, which is actually leraning rate. Learning rate value will be given manually. This value is how fast or how slow should our algorithm makes every iterations. We should not give very high or very low values, we will try to find the optimal value later.
# 
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=1OK7hNodJKNernY2m4iw7DnV0EHKBEbMV' 
#          style="width: 400px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 
# As you can see in update formula, we need to calculate derivatives of w and b according to loss function. Derivative formulas for w and b are like below. X is our x_train matrix, Y is our y_train matrix and g(X) is our y_head matrix. m is the sample number which is 248 for our data set and can be found as x_train.shape[1].
# 
# <figure>
#     <img src='https://drive.google.com/uc?export=view&id=1p0_C-Q-Su9eXo38pgauBxrOTMx64NvnB' 
#          style="width: 200px; max-width: 100%; height: auto"
#          alt='missing'/>
# </figure>
# 
# Let's write a function that calculates y_head, loss and cost values as forward propagation, and calculates derivatives of w and b as backpropagation.

# In[ ]:


def forward_backward_propagation(w,b,x_train,y_train):
    # forward propagation
    
    y_head = sigmoid(np.dot(w.T,x_train) + b)
    loss = -(y_train*np.log(y_head) + (1-y_train)*np.log(1-y_head))
    cost = np.sum(loss) / x_train.shape[1]
    
    # backward propagation
    derivative_weight = np.dot(x_train,((y_head-y_train).T))/x_train.shape[1]
    derivative_bias = np.sum(y_head-y_train)/x_train.shape[1]
    gradients = {"derivative_weight" : derivative_weight, "derivative_bias" : derivative_bias}
    
    return cost,gradients


# Forward_backward_propagation function calculates derivatives once. But we need to update w and b at every step according to update formula. So we call this function from a for loop that iterates according to a parameter we give.
# 
# I stored iteration number and cost value calculated at every step in an array, and plot the results to see which learning rate and iteration number combination gives the perfect match.

# In[ ]:


def update_weight_and_bias(w,b,x_train,y_train,learning_rate,iteration_num) :
    cost_list = []
    index = []
    
    #for each iteration, update w and b values
    for i in range(iteration_num):
        cost,gradients = forward_backward_propagation(w,b,x_train,y_train)
        w = w - learning_rate*gradients["derivative_weight"]
        b = b - learning_rate*gradients["derivative_bias"]
        
        cost_list.append(cost)
        index.append(i)

    parameters = {"weight": w,"bias": b}
    
    print("iteration_num:",iteration_num)
    print("cost:",cost)

    #plot cost versus iteration graph to see how the cost changes over number of iterations
    plt.plot(index,cost_list)
    plt.xlabel("Number of iteration")
    plt.ylabel("Cost")
    plt.show()

    return parameters, gradients


# Now it is time to make predictions. We trained our data, found the final and optimal w and b values according to our algorithm. Let's apply logistic regression formula for the x_test matrix and find predicted y_head values. I told that sigmoid function gives a probabilistic result, before. So we can say that if the probabilistic value is 0 or close to 0, than it is 0. Or if the probabilistic value is 1 or close to 1, than it is 1. So for every element of the array, I controlled if the value is smaller or bigger than 0.5, and find a final array includes predicted 0 and 1's.

# In[ ]:


def predict(w,b,x_test):
    z = np.dot(w.T,x_test) + b
    y_predicted_head = sigmoid(z)
    
    #create new array with the same size of x_test and fill with 0's.
    y_prediction = np.zeros((1,x_test.shape[1]))
    
    for i in range(y_predicted_head.shape[1]):
        if y_predicted_head[0,i] <= 0.5:
            y_prediction[0,i] = 0
        else:
            y_prediction[0,i] = 1
    return y_prediction


# Combine all written functions into a final function, and calculate the accuracy. For the accuracy, we compare values of existing y_test array and calculated y_prediction array. Both arrays include 0 and 1 values. So if same index of these arrays include same value, then it is true, otherwise it is wrong. We calculated how many indexes have different values and substract the mean of the result from 100. This gives the accuracy of our Solution 1 algorithm.

# In[ ]:


def logistic_regression(x_train,y_train,x_test,y_test,learning_rate,iteration_num):
    dimension = x_train.shape[0]#For our dataset, dimension is 248
    w,b = initialize_weights_and_bias(dimension)
    
    parameters, gradients = update_weight_and_bias(w,b,x_train,y_train,learning_rate,iteration_num)

    y_prediction = predict(parameters["weight"],parameters["bias"],x_test)
    
    # Print test Accuracy
    print("manuel test accuracy:",(100 - np.mean(np.abs(y_prediction - y_test))*100)/100)


# As I mentioned before, we will give some values to learning rate and number_of_iterations parameters.
# Start with learning_rate = 1 and number_of_iterations = 10

# In[ ]:


logistic_regression(x_train,y_train,x_test,y_test,1,10)


# Cost is 0.60 and accuracy is 70%. The cost is close to 0, so we are on the right way. Lets try different values to decrease cost value and increase accuracy.

# In[ ]:


logistic_regression(x_train,y_train,x_test,y_test,10,10)


# We increased learning rate so much, we expected algorithm to learn fast bu it did not happen. Because big moves caused the cost to go far away than the expected value.
# 
# Let's try one more;

# In[ ]:


logistic_regression(x_train,y_train,x_test,y_test,4,200)


# Compared to first try, I increased learning rate and iteration but not too much. Cost decreased and accuracy increased to %80. This result is fine for me. You can also write a function to make many iterations and find the highest accuracy.
# 
# We wrote so many codes for the algorithm. But luckily there is a library that makes all these calculations for us easily :)
# 
# **Solution 2 : Sklearn Library**
# With using sklearn library, we can create a logistic regression model and find the accuracy easliy like below:

# In[ ]:


from sklearn.linear_model import LogisticRegression
lr_model = LogisticRegression()

lr_model.fit(x_train.T,y_train.T)

print("sklearn test accuracy:", lr_model.score(x_test.T,y_test.T))


# Hope you like my kernel!

# 