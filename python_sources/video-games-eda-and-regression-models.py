#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# For data visualization
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns; sns.set()

# plotly
# import plotly.plotly as py
from plotly.offline import init_notebook_mode, iplot, plot
import plotly as py
init_notebook_mode(connected=True)
import plotly.graph_objs as go
import plotly.figure_factory as ff

# Disabling warnings
import warnings
warnings.simplefilter("ignore")

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 5GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session


# In[ ]:


data = pd.read_csv("/kaggle/input/videogamesales/vgsales.csv")
data1 = data.copy()


# # General Information about the dataset

# This dataset contains a list of video games with sales greater than 100,000 copies. It was generated by a scrape of vgchartz.com.
# 
# Fields include
# 
# Rank - Ranking of overall sales
# 
# Name - The games name
# 
# Platform - Platform of the games release (i.e. PC,PS4, etc.)
# 
# Year - Year of the game's release
# 
# Genre - Genre of the game
# 
# Publisher - Publisher of the game
# 
# NA_Sales - Sales in North America (in millions)
# 
# EU_Sales - Sales in Europe (in millions)
# 
# JP_Sales - Sales in Japan (in millions)
# 
# Other_Sales - Sales in the rest of the world (in millions)
# 
# Global_Sales - Total worldwide sales.

# In[ ]:


display(data1.head())
display(data1.tail())


# In[ ]:


data1.info()


# ### We see that there are nan values in year and publisher columns.

# In[ ]:


data1.isnull().sum()


# ### We check the unique values in categorical variables and years.

# In[ ]:


display(data1.Platform.unique())
display(data1.Genre.unique())
display(data1.Year.unique())


# In[ ]:


display(len(data1.Platform.unique()))
display(len(data1.Genre.unique()))
display(len(data1.Publisher.unique()))


# # Data Cleaning

# ### There is a category in Platform feature called 2600. When we look that in google search, we see that the actual name is Atari 2600. Thus, we replace 2600 with Atari.

# In[ ]:


data1['Platform'].replace('2600', 'Atari', inplace=True)


# ### We see that there is a gap between 2017 and 2020 and there is only one observation in 2020, so we drop that observation.

# In[ ]:


sorted((data1.Year.unique()))


# In[ ]:


data1[data1.Year>2017]


# In[ ]:


data1 = data1[data1.Year<2018]


# In[ ]:


data1.head()


# ### We check the observations with nan values. Although the number of observations with nan values is relatively low, I have decided to keep them. Therefore, we replace nan values in Publisher feature with Unknown, and nan values in Year feature with the most frequent year. 

# In[ ]:


data1[data1.Publisher.isna()]


# In[ ]:


data1.Publisher.fillna('Unknown', inplace=True)


# In[ ]:


data1.Year.fillna(data1.Year.mode()[0], inplace=True)


# In[ ]:


data1.isnull().sum()


# In[ ]:


data1.Year = data1.Year.astype('int64')
data1.head()


# In[ ]:


data1.info()


# # EDA

# In[ ]:


data1.describe().T


# ### As expected we have high correlation between the global sales and regional sales. Because, global sales is the sum of the regional sales. Thus, we cannot use these variables in our analysis and we need to use encoded categorical variables for ML analysis. 

# In[ ]:


data1.corr()


# ## Countplots of Categorical Variables

# In[ ]:


data1.head()


# In[ ]:


display(data1.Platform.value_counts())
display(data1.Genre.value_counts())
display(data1.Publisher.value_counts())


# ### DS and PS2 are the top 2 platforms for video games. 
# ### Action and Sports are the top 2 genres of video games.
# ### Electronic Arts is the top publisher of video games.

# In[ ]:


plt.subplots(1,1)
sns.countplot(data1.Platform, order=data1.Platform.value_counts().iloc[:14].index)
plt.xticks(rotation= 45)
plt.title("Video Games by Platform Top15",color = 'blue',fontsize=15)
plt.show()

plt.subplots(1,1)
sns.countplot(data1.Genre, order=data1.Genre.value_counts().index)
plt.title("Video Games by Genre",color = 'blue',fontsize=15)
plt.xticks(rotation= 75)
plt.show()

plt.subplots(1,1)
sns.countplot(data1.Publisher, order=data1.Publisher.value_counts().iloc[0:14].index)
plt.title("Video Games by Publisher Top15",color = 'blue',fontsize=15)
plt.xticks(rotation= 90)
plt.show()


# ## Global Video Game Sales by Categories

# ### Platform, shooter and role-playing are the top 3 genres by average global sales. 

# In[ ]:


# data1.groupby('Genre')['Global_Sales'].mean().sort_values(ascending=False)


# In[ ]:


order_genre = data1.groupby('Genre')['Global_Sales'].mean().sort_values(ascending=False).index
order_genre


# In[ ]:


plt.figure(figsize=(10, 5))
sns.barplot(x=data1.Genre, y=data1.Global_Sales, order=order_genre);
plt.xticks(rotation= 45)
plt.xlabel('Genre', fontsize=14)
plt.ylabel('Average Global Sales (Million)', fontsize=14)
plt.title('Average Global Sales by Genre', color = 'blue', fontsize=15)
plt.show()


# ### GB, NES and GEN are the top 3 platforms by average global sales.

# In[ ]:


# data1.groupby('Platform')['Global_Sales'].mean().sort_values(ascending=False).head(15)


# In[ ]:


order_platform = data1.groupby('Platform')['Global_Sales'].mean().sort_values(ascending=False).head(15).index
order_platform


# In[ ]:


plt.figure(figsize=(10, 5))
sns.barplot(x=data1.Platform, y=data1.Global_Sales, order=order_platform);
plt.xticks(rotation= 45)
plt.xlabel('Platform', fontsize=14)
plt.ylabel('Average Global Sales (Million)', fontsize=14)
plt.title('Average Global Sales by Platform Top15', color = 'blue', fontsize=15)
plt.show()


# ### Palcom, Red Orb, Nintendo are the top 3 publishers by average global sales.

# In[ ]:


# data1.groupby('Publisher')['Global_Sales'].mean().sort_values(ascending=False).head(15)


# In[ ]:


order_publisher = data1.groupby('Publisher')['Global_Sales'].mean().sort_values(ascending=False).head(15).index
order_publisher


# In[ ]:


plt.figure(figsize=(10, 5))
sns.barplot(x=data1.Publisher, y=data1.Global_Sales, order=order_publisher)
plt.xticks(rotation= 90)
plt.xlabel('Genre', fontsize=14)
plt.ylabel('Average Global Sales (Million)', fontsize=14)
plt.title('Average Global Sales by Publisher', color = 'blue', fontsize=15)
plt.show()


# ## Analysis of Global and Regional Sales

# ### As it is shown below through the histogram graph and kurtosis and skewness values regarding global sales, it is not normally distributed. In fact, the sales numbers for most of the games are below 1 million and there are also top selling video games in the data as well. Thus, it would be good to compare the regression model test errors before and after normalization of the data. 

# In[ ]:


trace1 = go.Histogram(
    x=data1.Global_Sales,
    opacity=0.75,
    name = "2011",
    marker=dict(color='rgba(171, 50, 96, 0.6)'))
data = [trace1]
layout = go.Layout(barmode='overlay',
                   title='global sales distribution',
                   xaxis=dict(title='Sales (Million)'),
                   yaxis=dict( title='Count'),
)
fig = go.Figure(data=data, layout=layout)
iplot(fig)


# In[ ]:


import scipy.stats as stats
stats.describe(data1.Global_Sales)


# ### There is steady increase in global sales until 2008-2009 and we see a decrease since then. However, we should be cautious about the sales in 2016 and 2017. There may some missing data there since we observe a sharp decrease in 2016 and very low level of sum of global sales in 2017.

# In[ ]:


# data1.groupby('Year')['Global_Sales'].sum()


# In[ ]:


global_sales_year = data1.groupby('Year')['Global_Sales'].sum()
global_sales_year_index = data1.groupby('Year')['Global_Sales'].sum().index


# In[ ]:


plt.figure(figsize=(15, 5))
sns.barplot(x=global_sales_year_index, y=global_sales_year)
plt.xticks(rotation= 45)
plt.xlabel('Genre', fontsize=14)
plt.ylabel('Global Sales (Million)', fontsize=14)
plt.title('Total Global Sales by Genre over the Years', color = 'blue', fontsize=15)
plt.show()


# ### When we look at the sum of global sales together with the regional sum of sales, we observe the increase in the share of NA Sales and EU Sales. 

# In[ ]:


data1.head()


# In[ ]:


na_sales_year = data1.groupby('Year')['NA_Sales'].sum()
na_sales_year_index = data1.groupby('Year')['NA_Sales'].sum().index
eu_sales_year = data1.groupby('Year')['EU_Sales'].sum()
eu_sales_year_index = data1.groupby('Year')['EU_Sales'].sum().index
jp_sales_year = data1.groupby('Year')['JP_Sales'].sum()
jp_sales_year_index = data1.groupby('Year')['JP_Sales'].sum().index
other_sales_year = data1.groupby('Year')['Other_Sales'].sum()
other_sales_year_index = data1.groupby('Year')['Other_Sales'].sum().index

# visualization
f,ax = plt.subplots(figsize = (15,10))
sns.barplot(y=global_sales_year, x=global_sales_year_index, color='yellow',alpha = 0.3,label='Global' )
sns.barplot(y=na_sales_year, x=na_sales_year_index,color='green',alpha = 0.5,label='NA' )
sns.barplot(y=eu_sales_year, x=eu_sales_year_index, color='blue',alpha = 0.5,label='EU')
sns.barplot(y=jp_sales_year, x=jp_sales_year_index,color='red',alpha = 0.7,label='JP')
sns.barplot(y=other_sales_year, x=other_sales_year_index, color='cyan',alpha = 0.5,label='Other')

plt.xticks(rotation= 45)
ax.legend(loc='upper right',frameon = True)
ax.set(xlabel='Year', ylabel='Sales (Million)',title = "Global and Regional Total Sales over the Years")
plt.show()


# In[ ]:


import plotly.graph_objs as go

trace1 = go.Scatter(
                    x = global_sales_year_index,
                    y = global_sales_year,
                    mode = "lines",
                    name = "Global")
trace2 = go.Scatter(
                    x = global_sales_year_index,
                    y = na_sales_year,
                    mode = "lines+markers",
                    name = "NA")


trace3 = go.Scatter(
                    x = global_sales_year_index,
                    y = eu_sales_year,
                    mode = "lines",
                    name = "EU",
                    line = dict(dash="dot"))

trace4 = go.Scatter(
                    x = global_sales_year_index,
                    y = jp_sales_year,
                    mode = "lines",
                    name = "JP",
                    line = dict(dash="dash"))

trace5 = go.Scatter(
                    x = global_sales_year_index,
                    y = other_sales_year,
                    mode = "lines",
                    name = "Other")


data = [trace1, trace2, trace3, trace4, trace5]
layout = dict(title = 'Global and Regional Total Sales over the Years',
              xaxis= dict(title= 'Year',ticklen= 5,zeroline= False), 
              yaxis= dict(title= 'Millon',ticklen= 5,zeroline= False))
fig = dict(data = data, layout = layout)
iplot(fig)


# ### As it can be seen from the pie-chart below that NA has the largest share in cumulative global sales between 1980-2016. The sales revenue from NA is almost half of the global sales. Sales in EU is the second with approximately the quarter of global sales. Thus, these two regions are the most defining regions in global sales. 

# In[ ]:


sales_region = [data1.NA_Sales.sum(),data1.EU_Sales.sum(),data1.JP_Sales.sum(),data1.Other_Sales.sum()]
labels = ['NA', 'EU', 'JP', 'Other']
colors = ['cyan','red','yellow','green']

# visual
plt.figure(figsize = (7,7))
plt.pie(sales_region, labels=labels, colors=colors, autopct='%1.1f%%')
plt.title('Total Share of Regions in Global Sales', color = 'blue', fontsize = 15)
plt.show()


# ### Action, sports, shooter, role-playing and platform games are the top 5 video games in global sales. 

# In[ ]:


global_sales_genre = data1.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False)
order_sales_genre = data1.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False).index

plt.figure(figsize=(15, 5))
sns.barplot(x=order_sales_genre, y=global_sales_genre, order=order_sales_genre)
plt.xticks(rotation= 0)
plt.xlabel('Genre', fontsize=14)
plt.ylabel('Global Sales (Million)', fontsize=14)
plt.title('Global Sales by Genre', color = 'blue', fontsize=15)
plt.show()


# ### PS2, X360, PS3, Wii and DS are the top 5 platforms with respect to total global sales. 

# In[ ]:


global_sales_platform = data1.groupby('Platform')['Global_Sales'].sum().sort_values(ascending=False).iloc[0:10]
order_sales_platform = global_sales_platform.index

plt.figure(figsize=(15, 5))
sns.barplot(x=order_sales_platform, y=global_sales_platform, order=order_sales_platform)
plt.xticks(rotation= 0)
plt.xlabel('Platform', fontsize=14)
plt.ylabel('Global Sales (Million)', fontsize=14)
plt.title('Global Sales by Platform', color = 'blue', fontsize=15)
plt.show()


# ### Nintendo, Electronic Arts, Activision, Sony and Ubisoft are the top 5 platforms with respect to total global sales.

# In[ ]:


global_sales_platform = data1.groupby('Publisher')['Global_Sales'].sum().sort_values(ascending=False).iloc[0:10]
order_sales_platform = global_sales_platform.index

plt.figure(figsize=(15, 5))
sns.barplot(x=order_sales_platform, y=global_sales_platform, order=order_sales_platform)
plt.xticks(rotation= 60)
plt.xlabel('Publisher', fontsize=14)
plt.ylabel('Global Sales (Million)', fontsize=14)
plt.title('Global Sales by Publisher', color = 'blue', fontsize=15)
plt.show()


# In[ ]:


# na_sales_year_genre = data1.pivot_table(index='Year',columns='Genre', aggfunc = {'NA_Sales': sum})
# na_sales_year_genre


# # Linear Regression Models
# ### Our dependent variable is global sales and it will be our main focus to make predictions through different linear regression models. 
# ### As mentioned earlier, we do not have quantitative independent variables for regression analysis. Regional sales are just the sub-totals of global sales. They are highly correlated with the dependent variable. Thus, we need to convert our categorical variables, Platform, Genre and Publisher, into numerical variables and use them in the regression models.
# ### I am using the label encoding approach here. I am aware of the fact that it is not the most desired approach for categorical encoding since it has the disadvantage of misinterpretation by algorithms as having some sort of order in them. But, in one-hot method we have the dummy variable trap and curse of dimensionality problems as we have a lot of sub-categories in each of our categorical variables. 
# ### In this framework, I stick to label encoding approach. 

# In[ ]:


from sklearn.preprocessing import LabelEncoder


# In[ ]:


# label encoding of categorical variables
lbe = LabelEncoder()
data1['Genre_Cat'] = lbe.fit_transform(data1['Genre'])
data1['Platform_Cat'] = lbe.fit_transform(data1['Platform'])
data1['Publisher_Cat'] = lbe.fit_transform(data1['Publisher'])
data1.head()


# ## Multilinear Regression

# In[ ]:


from sklearn.preprocessing import StandardScaler
from sklearn import preprocessing
import statsmodels.api as sm 
import statsmodels.formula.api as smf 
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict 
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# ### Defining data and splitting with normalization

# In[ ]:


data2 = data1.loc[:,'Global_Sales':]
data2.head()


# In[ ]:


# Defining independent and dependent variables and splitting the data into two groups as train and test data
data2 = preprocessing.normalize(data2)
x = data2[:,1:]
y = data2[:,0]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, random_state= 42)


# ### Defining data and splitting without normalization as an alternative for comparison

# In[ ]:


# Defining independent and dependent variables and splitting the data into two groups as train and test data
# x = data1[['Genre_Cat','Platform_Cat','Publisher_Cat']]
# y = data1['Global_Sales']

# x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.20, random_state= 42)


# ### Statmodels

# In[ ]:


# Multilinear Regression model woth statmodels and model summary
lm = sm.OLS(y_train, x_train)
model = lm.fit()
model.summary()


# ### Sci Kit Learn

# In[ ]:


# Multilinear Regression model with skilearn 
lm1 = LinearRegression()
model1 = lm1.fit(x_train, y_train)


# In[ ]:


# Coefficients
model1.coef_ 


# In[ ]:


# Intercept
model1.intercept_


# In[ ]:


# R2 score
model1.score(x,y)


# In[ ]:


# RMSE score of train data
rmse = np.sqrt(mean_squared_error(y_train, model1.predict(x_train)))
rmse


# In[ ]:


# RMSE score of test data
rmse = np.sqrt(mean_squared_error(y_test, model1.predict(x_test)))
rmse


# ### Cross Validation

# In[ ]:


# RMSE average score of train data after cross-validation
np.sqrt(-cross_val_score(model1, 
                x_train, 
                y_train, 
                cv = 10, 
                scoring = "neg_mean_squared_error")).mean()


# In[ ]:


# R2 average for differents situation since each time the algorithm selects different %80 as train data 
cross_val_score(model1, x_train, y_train, cv = 10, scoring = "r2").mean()


# In[ ]:


# RMSE average score of test data after cross-validation
reg_final_rmse = np.sqrt(-cross_val_score(model1, 
                x_test, 
                y_test, 
                cv = 10, 
                scoring = "neg_mean_squared_error")).mean()
reg_final_rmse


# In[ ]:


# R2 average of test data after cross validation
reg_final_r2 = cross_val_score(model1, x_test, y_test, cv = 10, scoring = "r2").mean()
reg_final_r2


# ## PCA

# In[ ]:


from sklearn.decomposition import PCA
from sklearn.preprocessing import scale 


# In[ ]:


# PCA model instantiation and transformation for PCA
pca = PCA()
x_reduced_train = pca.fit_transform(scale(x_train))


# In[ ]:


# PCA components 
x_reduced_train[0:1,:]


# In[ ]:


# Cumulative percentage of explained variance as we add each component
np.cumsum(np.round(pca.explained_variance_ratio_, decimals = 4)*100)[0:5]


# In[ ]:


# PCA instantiation of regression model
lm2 = LinearRegression()
pcr_model = lm2.fit(x_reduced_train, y_train)


# In[ ]:


# PCA model intercept
pcr_model.intercept_


# In[ ]:


# PCA model coefficients
pcr_model.coef_


# In[ ]:


# PCA Regression model with statmodels
lm3 = sm.OLS(y_train, x_reduced_train)
model2 = lm3.fit()
model2.summary()


# In[ ]:


# PCA model prediction
y_pred = pcr_model.predict(x_reduced_train)


# In[ ]:


# PCA RMSE score for train data
np.sqrt(mean_squared_error(y_train, y_pred))


# In[ ]:


# PCA R2 for train data
r2_score(y_train, y_pred)


# In[ ]:


# PCA instantiation of model for test data
pca2 = PCA()
x_reduced_test = pca2.fit_transform(scale(x_test))


# In[ ]:


# PCA prediction with test data
y_pred = pcr_model.predict(x_reduced_test)


# In[ ]:


# PCA RMSE score for test data
pca_final_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
pca_final_rmse


# In[ ]:


# PCA R2 for test data
pca_final_r2 = r2_score(y_test, y_pred)
pca_final_r2


# ### Model Tuning

# In[ ]:


from sklearn import model_selection


# In[ ]:


# Illustraion of chage in RMSE score as we add each component into the model.

cv_10 = model_selection.KFold(n_splits = 10,
                             shuffle = True,
                             random_state = 1)

lm4 = LinearRegression()

RMSE = []

for i in np.arange(1, x_reduced_train.shape[1] + 1):
    
    score = np.sqrt(-1*model_selection.cross_val_score(lm4, 
                                                       x_reduced_train[:,:i], 
                                                       y_train.ravel(), 
                                                       cv=cv_10, 
                                                       scoring='neg_mean_squared_error').mean())
    RMSE.append(score)


# In[ ]:


# We see that the RMSE score decreases as we add all three components into the model.
# So, we can decide to keep all three components in the model.
plt.plot(RMSE, '-v')
plt.xlabel('Number of Components')
plt.ylabel('RMSE')
plt.title('PCR Model Tuning');


# ## PLS Regression

# In[ ]:


from sklearn.cross_decomposition import PLSRegression, PLSSVD


# In[ ]:


# PLS model instantiation
pls_model = PLSRegression().fit(x_train, y_train)


# In[ ]:


# PLS model coefficients
pls_model.coef_


# In[ ]:


# PLS model predictions based on train data
y_pred = pls_model.predict(x_train)


# In[ ]:


# PLS RMSE score for train data
np.sqrt(mean_squared_error(y_train, y_pred))


# In[ ]:


# PLS R2 for train data
r2_score(y_train, y_pred)


# In[ ]:


# PLS prediction based on test data
y_pred = pls_model.predict(x_test)


# In[ ]:


# PLS RMSE test score
np.sqrt(mean_squared_error(y_test, y_pred))


# In[ ]:


# PLS R2 for test data
r2_score(y_test, y_pred)


# ### PLS Cross Validation

# In[ ]:


# Illustraion of change in RMSE score as the model adds one additional component to the model in each loop.
cv_10 = model_selection.KFold(n_splits=10, shuffle=True, random_state=1)


RMSE = []

for i in np.arange(1, x_train.shape[1] + 1):
    pls = PLSRegression(n_components=i)
    score = np.sqrt(-1*cross_val_score(pls, x_train, y_train, cv=cv_10, scoring='neg_mean_squared_error').mean())
    RMSE.append(score)

plt.plot(np.arange(1, x_train.shape[1] + 1), np.array(RMSE), '-v', c = "r")
plt.xlabel('Number of Components')
plt.ylabel('RMSE')
plt.title('Components and RMSE');


# In[ ]:


# PLS model with two components
pls_model2 = PLSRegression(n_components = 3).fit(x_train, y_train)


# In[ ]:


# PLS prediction based on test data after cross validation
y_pred2 = pls_model2.predict(x_test)


# In[ ]:


# PLS RMSE test score after cross validation
pls_final_rmse = np.sqrt(mean_squared_error(y_test, y_pred2))
pls_final_rmse


# In[ ]:


pls_final_r2 = r2_score(y_test, y_pred2)
pls_final_r2


# ## Ridge Regression

# In[ ]:


from sklearn.linear_model import Ridge


# In[ ]:


# Ridge model instantiation and model details
ridge_model = Ridge(alpha = 0.1).fit(x_train, y_train)
ridge_model


# In[ ]:


# Ridge model details
ridge_model.coef_


# In[ ]:


# Illustration of how weights of independent variables approaches to 0 as the alpha value increases. 

lambdas = 10**np.linspace(10,-2,100)*0.5

ridge_model = Ridge()
coefficients = []

for i in lambdas:
    ridge_model.set_params(alpha = i)
    ridge_model.fit(x_train, y_train) 
    coefficients.append(ridge_model.coef_)
        
ax = plt.gca()
ax.plot(lambdas, coefficients) 
ax.set_xscale('log') 

plt.xlabel('Lambda(Alpha) Values')
plt.ylabel('Coefficients')
plt.title('Ridge Coefficients');


# In[ ]:


# Ridge prediction based on test data
y_pred = ridge_model.predict(x_test)


# In[ ]:


# Ridge RMSE test score
np.sqrt(mean_squared_error(y_test, y_pred))


# In[ ]:


# Ridge R2 
r2_score(y_test, y_pred)


# ### Ridge Regression Cross Validation

# In[ ]:


from sklearn.linear_model import RidgeCV


# In[ ]:


# Ridge instantiation of cross validation model and model details
ridge_cv = RidgeCV(alphas = lambdas, 
                   scoring = "neg_mean_squared_error",
                   normalize = True)
ridge_cv.fit(x_train, y_train)
ridge_model


# In[ ]:


# Ridge cross validation alpha score
ridge_cv.alpha_


# In[ ]:


# Ridge tuned model after cross validation
ridge_tuned = Ridge(alpha = ridge_cv.alpha_, 
                   normalize = True).fit(x_train,y_train)


# In[ ]:


# Ridge model coefficients after cross validation
ridge_tuned.coef_


# In[ ]:


# Ridge RMSE test score after cross validation
ridge_final_rmse = np.sqrt(mean_squared_error(y_test, ridge_tuned.predict(x_test)))
ridge_final_rmse


# In[ ]:


# Ridge R2 after cross validation
ridge_final_r2 = r2_score(y_test, ridge_tuned.predict(x_test))
ridge_final_r2


# ## Lasso Regression

# In[ ]:


from sklearn.linear_model import Lasso


# In[ ]:


# Lasso model instantation and model details
lasso_model = Lasso(alpha = 1.0).fit(x_train, y_train)
lasso_model


# In[ ]:


# Lasso model coefficients
lasso_model.coef_


# In[ ]:


# The weight of independent variables comes to value of zero as the alpha score changes. 
# However, we cannot see this change since we have coefficients close to 0 before cross validation. 

lasso = Lasso()
lambdas = 10**np.linspace(10,-2,100)*0.5 
coefficients = []

for i in lambdas:
    lasso.set_params(alpha=i)
    lasso.fit(x_train, y_train)
    coefficients.append(lasso.coef_)
    
ax = plt.gca()
ax.plot(lambdas*2, coefficients)
ax.set_xscale('log')
plt.axis('tight')
plt.xlabel('alpha')
plt.ylabel('weights')


# In[ ]:


# Lasso model prediction based on test data
y_pred = lasso_model.predict(x_test)


# In[ ]:


# Lasso RMSE score
np.sqrt(mean_squared_error(y_test, y_pred))


# In[ ]:


# Lasso R2
r2_score(y_test, y_pred)


# ### Lasso Regression Cross Validation

# In[ ]:


from sklearn.linear_model import LassoCV


# In[ ]:


# Lasso instantiation of cross validation model
lasso_cv_model = LassoCV(alphas = None, 
                         cv = 10, 
                         max_iter = 10000, 
                         normalize = True)


# In[ ]:


# Lasso cross validation model details
lasso_cv_model.fit(x_train,y_train)


# In[ ]:


# Lasso cross validation model alpha score
lasso_cv_model.alpha_


# In[ ]:


# Lasso tuned model after cross validation
lasso_tuned = Lasso(alpha = lasso_cv_model.alpha_)
lasso_tuned.fit(x_train, y_train)


# In[ ]:


# Lasso predictions of tuned model base on test data
y_pred = lasso_tuned.predict(x_test)


# In[ ]:


# Lasso model coefficients after cross validation
lasso_tuned.coef_


# In[ ]:


# Lasso RMSE test score after cross validation
lasso_final_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
lasso_final_rmse


# In[ ]:


# Lasso R2 after cross validation
lasso_final_r2 = r2_score(y_test, y_pred)
lasso_final_r2


# ## ElasticNet Regression

# In[ ]:


from sklearn.linear_model import ElasticNet


# In[ ]:


# Elasticnet model instantiation
enet_model = ElasticNet().fit(x_train, y_train)


# In[ ]:


# Elasticnet model coefficients
enet_model.coef_


# In[ ]:


#  Elasticnet intercept
enet_model.intercept_


# In[ ]:


# Elasticnet model details
enet_model


# In[ ]:


# Elasticnet model predictions based on test data
y_pred = enet_model.predict(x_test)


# In[ ]:


# Elasticnet RMSE test score
np.sqrt(mean_squared_error(y_test, y_pred))


# In[ ]:


# Elasticnet R2
r2_score(y_test, y_pred)


# ### Elasticnet Regression Cross Validation

# In[ ]:


from sklearn.linear_model import ElasticNetCV


# In[ ]:


# Elasticnet cross validation model instantiation
enet_cv_model = ElasticNetCV(cv = 10, random_state = 0).fit(x_train, y_train)


# In[ ]:


# Elasticnet cross validation alpha value
enet_cv_model.alpha_


# In[ ]:


# Elasticnet cross validation model details
enet_cv_model


# In[ ]:


# Elasticnet tuned model based on alpha score
enet_tuned = ElasticNet(alpha = enet_cv_model.alpha_).fit(x_train,y_train)


# In[ ]:


# Elasticnet predictions based on the tuned model
y_pred = enet_tuned.predict(x_test)


# In[ ]:


# Elasticnet model coefficients after cross validation
enet_tuned.coef_


# In[ ]:


# Elasticnet RMSE test score after cross validation
enet_final_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
enet_final_rmse


# In[ ]:


# Elasticnet R2 after cross validation
enet_final_r2 = r2_score(y_test, y_pred)
enet_final_r2


# In[ ]:


print(f"""Multilinear Regression RMSE: {reg_final_rmse}, R2: {reg_final_r2}
PCA Regression RMSE: {pca_final_rmse}, R2: {pca_final_r2}
PLS Regression RMSE: {pls_final_rmse}, R2: {pls_final_r2}
Ridge Regression RMSE: {ridge_final_rmse}, R2: {ridge_final_r2}
Lasso Regression RMSE: {lasso_final_rmse}, R2: {lasso_final_r2}
ElasticNet Regression RMSE: {enet_final_rmse}, R2: {enet_final_r2}""")


# ### Comparison of RMSE and R2 values across different models with normalization

# * __Multilinear Regression RMSE__: 0.015001624864342897, __R2__: 0.07397442844946144
# * __PCA Regression RMSE__        : 0.01674123699336149,  __R2__: 0.09509144293622152
# * __PLS Regression RMSE__        : 0.016741898509377524, __R2__: 0.09501992810961701
# * __Ridge Regression RMSE__      : 0.016739899842261558, __R2__: 0.09523599033741226
# * __Lasso Regression RMSE__      : 0.016741833987041262, __R2__: 0.0950269035808824
# * __ElasticNet Regression RMSE__ : 0.0167404713962502,   __R2__: 0.09517420617962535

# ### Comparison of RMSE and R2 values across different models without normalization

# * __Multilinear Regression RMSE__: 1.7105964805711504, __R2__: -0.015022400745020936
# * __PCA Regression RMSE__: 2.0668894045476174, __R2__: -0.00018219613950942737
# * __PLS Regression RMSE__: 2.0646621120360353, __R2__: 0.0019722471705171385
# * __Ridge Regression RMSE__: 2.0649740466339517, __R2__: 0.0016706550587132218
# * __Lasso Regression RMSE__: 2.0646617632879796, __R2__: 0.0019725843300040236
# * __ElasticNet Regression RMSE__: 2.0647315517730767, __R2__: 0.0019051137158706544

# # Polynomial Regression

# ### We get lower RMSE test scores and much higher R2 values with polynomial regression model. 
# ### We can do model tuning by changing the degree and it looks that degree = 3 is the ideal value since we have a lower RMSE. 

# In[ ]:


from sklearn.preprocessing import PolynomialFeatures


# In[ ]:


# we change the degree value for model tuning
poly_features = PolynomialFeatures(degree=3)


# In[ ]:


x_train_poly = poly_features.fit_transform(x_train)


# In[ ]:


poly_model = LinearRegression()
poly_model.fit(x_train_poly, y_train)


# In[ ]:


y_train_pred = poly_model.predict(x_train_poly)


# In[ ]:


# Polynomial Regression RMSE score for train data
rmse_train = np.sqrt(mean_squared_error(y_train,y_train_pred))
r2_train = r2_score(y_train, y_train_pred)
print(rmse_train,r2_train)


# In[ ]:


y_test_pred = poly_model.predict(poly_features.fit_transform(x_test))


# In[ ]:


# Polynomial Regression RMSE score for test data
rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
r2_test = r2_score(y_test, y_test_pred)
print(rmse_test,r2_test)


# * __degree__ = 2; __RMSE__ = 0.007746125544948684, __R2__ = 0.8062692011851837
# * __degree__ = 3; __RMSE__ = 0.0075387615891847806, __R2__ = 0.816502722805112
# * __degree__ = 4; __RMSE__ = 0.007870531850137641, __R2__ = 0.7999964208296635

# # Conclusion:
# ### The data is not the most desired data since we do not have quantitative independent variables and we have to encode categorical variables. As we have a lot of sub-categories, it would a better approach to use label encoding. However, this approach has some downsides as mentioned above.
# ### I have tried to use the most prominent linear regression models and compared them with and without normalized data. 
# ### Multilinear Regression has better RMSE test scores and the rest of the approaches have very close RMSE test scores. In this respect, Multilinear Regression model appears to be the best model compared to others. Ridge Regression follows the former, if we check the decimals. 
# ### On the other hand, we have very low R2 values in linear regression models.
# ### Finally, I have used polynomial regression model. We see that we have more robust model with polynomial regression model with respect to both RMSE test score and R2 value. And when we check these values at different degrees, it looks like that 3rd degree has a lower RMSE. 

# In[ ]:



