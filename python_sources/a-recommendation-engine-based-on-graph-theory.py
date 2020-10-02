#!/usr/bin/env python
# coding: utf-8

# This kernel is based on Andrea Gigli's suggestion of using bipartite complex networks to build a recommendation engine (https://www.slideshare.net/andrgig/recommendation-systems-in-banking-and-financial-services). Although I did my best in commenting the code, I strongly encourage you to go through his slides before diving into the code. After building the network per his methodology I ran community detection algorithms to find products that are often purchased together. These clusters of products can then be used to make suitable suggestions to a customer after he purchases (or puts on his online basket) his very first product. 
# Although I use only a very small subset of the UCI repository the clusters tend to contain similar products either in category (e.g. same products in different colors) or area of use (e.g. kitchen-related stuff). I include a couple of snapshots from Gephi (graph visuallization software) that really makes your life easier when handling and studying graphs. 

# In[ ]:


# Import libraries
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


#Import data set 
df = pd.read_excel('../input/Online Retail.xlsx', header = 0)


# In[ ]:


print('dataset dimensions are:', df.shape)
df.describe(include = 'all')


# In[ ]:


#Let's take a smaller set of the data to speed up computations for this example
df_sample = df.iloc[:200] 


# In[ ]:


#Data pre-processing 

#Delete rows with no Customer ID (if there is such a case)
cleaned_retail = df_sample.loc[pd.isnull(df_sample.CustomerID) == False]

#Create a lookup table
item_lookup = cleaned_retail[['StockCode', 'Description']].drop_duplicates()
item_lookup['StockCode'] = item_lookup.StockCode.astype(str)

#Do some 'data cleaning' to raw data
cleaned_retail['CustomerID'] = cleaned_retail.CustomerID.astype(int)
cleaned_retail = cleaned_retail[['StockCode', 'Quantity', 'CustomerID']]
grouped_cleaned = cleaned_retail.groupby(['CustomerID', 'StockCode']).sum().reset_index()
grouped_cleaned.Quantity.loc[grouped_cleaned.Quantity == 0] = 1
grouped_purchased = grouped_cleaned.query('Quantity > 0')


# In[ ]:


#Count number of products and number of customers in the reduced dataset 
no_products = len(grouped_purchased.StockCode.unique())
no_customers = len(grouped_purchased.CustomerID.unique())
print('Number of customers in dataset:', no_customers)
print('Number of products in dataset:', no_products)


# In[ ]:


#Turn raw data to pivot ('ratings' matrix)
ratings = grouped_purchased.pivot(index = 'CustomerID', columns='StockCode', values='Quantity').fillna(0).astype('int')
#Binarize the ratings matrix (indicate only if a customer has purchased a product or not)
ratings_binary = ratings.copy()
ratings_binary[ratings_binary != 0] = 1


# In[ ]:


#Initialize zeros dataframe for product interactions
products_integer = np.zeros((no_products,no_products))

#Count how many times each product pair has been purchased
print('Counting how many times each pair of products has been purchased...')
for i in range(no_products):
    for j in range(no_products):
        if i != j:
            df_ij = ratings_binary.iloc[:,[i,j]] #create a temporary df with only i and j products as columns
            sum_ij = df_ij.sum(axis=1)
            pairings_ij = len(sum_ij[sum_ij == 2]) #if s1_ij == 2 it means that both products were purchased by the same customer
            products_integer[i,j] = pairings_ij
            products_integer[j,i] = pairings_ij


# In[ ]:


#Count how many customers have purchased each item
print('Counting how many times each individual product has been purchased...')
times_purchased = products_integer.sum(axis = 1)


# In[ ]:


#Construct final weighted matrix of item interactions
print('Building weighted product matrix...')
products_weighted = np.zeros((no_products,no_products))
for i in range(no_products):
    for j in range(no_products):
        if (times_purchased[i]+times_purchased[j]) !=0: #make sure you do not divide with zero
            products_weighted[i,j] = (products_integer[i,j])/(times_purchased[i]+times_purchased[j])


# In[ ]:


#Get list of item labels (instead of Codes)
nodes_codes = np.array(ratings_binary.columns).astype('str')
item_lookup_dict = pd.Series(item_lookup.Description.values,index=item_lookup.StockCode).to_dict()
nodes_labels = [item_lookup_dict[code] for code in nodes_codes]


# In[ ]:


#Create Graph object using the weighted product matrix as adjacency matrix
G = nx.from_numpy_matrix(products_weighted)
pos=nx.random_layout(G)
labels = {}
for idx, node in enumerate(G.nodes()):
    labels[node] = nodes_labels[idx]

nx.draw_networkx_nodes(G, pos , node_color="skyblue", node_size=30)
nx.draw_networkx_edges(G, pos,  edge_color='k', width= 0.3, alpha= 0.5)
nx.draw_networkx_labels(G, pos, labels, font_size=4)
plt.axis('off')
plt.show() # display


# Not very insightful right now, is it? Dont worry, we' ll get a clearer insight with the Gephi visualization down below. 
# 

# In[ ]:


#Export graph to Gephi
H=nx.relabel_nodes(G,labels) #create a new graph with Description labels and save to Gephi for visualizations
nx.write_gexf(H, "products.gexf")


# In[ ]:


#Find communities of nodes (products)
partition = community_louvain.best_partition(G, resolution = 1.5)
values = list(partition.values())


# In[ ]:


#Check how many communities were created
print('Number of communities:', len(np.unique(values)))


# In[ ]:


#Create dataframe with product description and community id
products_communities = pd.DataFrame(nodes_labels, columns = ['product_description'])
products_communities['community_id'] = values


# In[ ]:


#Lets take a peek at community 1
products_communities[products_communities['community_id']==1].head(15)


# And that's about it! We end up with a dataframe that contains products and the cluster they belong to! Now to make a suitable suggestion we only need to select one or more products that the customer has purchased (or is thinking of purchasing) and complement his final basket of goods. Happy customers and happy vendors!
# I include below the Gephi output:
# 
# 
# 

# The following image contains the entire network of products. The derived communities are easily distinguishable. 
# https://drive.google.com/open?id=1C1IvOxfe2Kt31Hrn7DjT-WuzZaKphFN_
# 

# This image zooms in the 'red' community. We can clearly see some patterns (e.g. 'bath' block word, 'love' block word, 'home' block word, etc...). https://drive.google.com/open?id=11_1g033XcFHKSF5c00VVX2D0cme8DL0G

# This image zooms in the 'black' community. This community contains kitchen-related stuff like cutlery sets, cake cases, paper paltes, lunch bags, etc.  https://drive.google.com/open?id=1TmSgEgDav2RtxyGbxM5E6WpSMPrv9RQ3

# In[1]:


#Lets now divide each element in products_weighted dataframe with the maximum of each row.
#This will normalize values in the row and we can perceive it as the possibility af a customer also buying
#product in column j after showing interest for the product in row i

#Turn into dataframe
products_weighted_pd = pd.DataFrame(products_weighted, columns = nodes_labels)
products_weighted_pd.set_index(products_weighted_pd.columns, 'product', inplace=True)

products_prob = products_weighted_pd.divide(products_weighted_pd.max(axis = 1), axis = 0)


# In[ ]:


#Now lets select a hypothetical basket of goods (one or more products) that a customer has already purchased or
#shown an interest for by clicking on an add or something, and then suggest him relative ones
basket = ['HOME BUILDING BLOCK WORD']
#Also select the number of relevant items to suggest
no_of_suggestions = 3

all_of_basket = products_prob[basket]
all_of_basket = all_of_basket.sort_values(by = basket, ascending=False)
suggestions_to_customer = list(all_of_basket.index[:no_of_suggestions])

print('You may also consider buying:', suggestions_to_customer)


# At this point I would like to remind you that we only used the first 200  rows of the data set. Still, this methodology performed really well! In my PC i have worked with much more data and the results are impressive. Many, many thanks and big respect to Andrea Gigli for this. Please do commend with any ideas on how to extend this kernel and keep these thumbs up for more!