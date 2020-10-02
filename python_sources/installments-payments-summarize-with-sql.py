#!/usr/bin/env python
# coding: utf-8

# # Home Credit Defoult Risk / installments_payments
# 

# In the Home Credit Default Risk project, we try to calculate the probability of a person applying to the credit institution to default in the loan payment process.

# ## Explanation of This Kernel

# We will transfer the information about each SK_ID_CURR from the sub-tables to the application_train / test tables, which we will use for machine learning.
# We will ensure that all information about each SK_ID_CURR is contained in a single line.
# So, by doing some aggregation operations or various encoding operations, we will summarize the information in the tables for each SK_ID_CURR.
# 
# In this kernel, I will only summarize the information for the installments_payments table. Of course many other variables can be derived. This notebook is just for example.
# 
# Firstly; installments_payments table contains information about loan installments.
# 
# My overall purpose in this kernel is to do feature engineering, aggregation operations and proportioning using information such as the number of loans, the number of loan installments, how much the borrower paid, and the duration of the loan installment payment.
# 
# I tried to code as simple and understandable as I could. I hope that will be useful.

# First of all, in order to do this work with SQL, you need to create a database and keep the tables in this database, which you will work on.

# Before you can write and run SQL queries in jupyterlab, you have to define your database and SQL as a query language.

# - installments_payments_1
# 
#   I noticed that there are several different records for a single installment of some loans. I have optimized these records in this table, as this will lead to incorrect analysis. In this process, I took great care to do this with the least amount of information loss.

# - installments_payments_2
# 
#   In this table, I did some feature engineering operations with some aggregation operations.

# - installments_payments_3
# 
#   In this last table, I also did feature engineering with some aggregation operations and some proportioning operations.
#   
#   As a result, in this table containing the information to be extracted into the previous_application table, the information about each SK_ID_CURR is summarized in a single line.

# In[ ]:


get_ipython().run_cell_magic('!', '', 'pip install --trusted-host pypi.org ipython-sql')


# In[ ]:


get_ipython().run_line_magic('load_ext', 'sql')


# In[ ]:


get_ipython().run_line_magic('sql', 'sqlite:///Home_credit_database.db')


# In[ ]:


get_ipython().run_cell_magic('sql', '', 'CREATE TABLE installments_payments_1 AS\nSELECT DISTINCT A.SK_ID_CURR, A.SK_ID_PREV, A.NUM_INSTALMENT_NUMBER, \n       A.DAYS_INSTALMENT, A.DAYS_ENTRY_PAYMENT, A.NUM_INSTALMENT_VERSION, \n       CASE WHEN A.SUM_INSTALMENT/2 BETWEEN B.SUM_PAYMENT-1 AND B.SUM_PAYMENT+1 THEN A.SUM_INSTALMENT/2 \n            ELSE A.SUM_INSTALMENT END SUM_INSTALLMENT, B.SUM_PAYMENT\nFROM\n    (\n    SELECT A.SK_ID_CURR, A.SK_ID_PREV, A.NUM_INSTALMENT_VERSION, A.NUM_INSTALMENT_NUMBER, \n           A.DAYS_INSTALMENT, A.DAYS_ENTRY_PAYMENT, SUM(A.AMT_INSTALMENT) SUM_INSTALMENT\n    FROM\n    installments_payments A, \n                            (\n                            SELECT SK_ID_CURR, SK_ID_PREV, NUM_INSTALMENT_NUMBER, \n                                COUNT(DISTINCT NUM_INSTALMENT_VERSION) CNT_DIFF_VERSION,\n                                COUNT( DISTINCT DAYS_INSTALMENT) CNT_DIFF_DAYS_INSTALLMENT, \n                                COUNT(DISTINCT DAYS_ENTRY_PAYMENT) CNT_DIFF_DAYS_PAYMENT, \n                                COUNT(DISTINCT AMT_INSTALMENT) CNT_DIFF_INSTALMENT,\n                                COUNT(DISTINCT AMT_PAYMENT) CNT_DIFF_PAYMENT\n                            FROM\n                            installments_payments\n                            GROUP BY\n                            SK_ID_CURR, SK_ID_PREV, NUM_INSTALMENT_NUMBER\n                            )B\n    ON\n    A.SK_ID_PREV=B.SK_ID_PREV\n    AND\n    A.NUM_INSTALMENT_NUMBER=B.NUM_INSTALMENT_NUMBER\n    GROUP BY\n    A.SK_ID_CURR, A.SK_ID_PREV, A.NUM_INSTALMENT_NUMBER, \n        CASE WHEN B.CNT_DIFF_VERSION=B.CNT_DIFF_INSTALMENT AND \n                    B.CNT_DIFF_DAYS_PAYMENT<> B.CNT_DIFF_DAYS_INSTALLMENT THEN A.DAYS_ENTRY_PAYMENT\n             WHEN B.CNT_DIFF_VERSION=B.CNT_DIFF_INSTALMENT AND \n                    B.CNT_DIFF_DAYS_PAYMENT= B.CNT_DIFF_DAYS_INSTALLMENT THEN A.DAYS_ENTRY_PAYMENT\n             WHEN B.CNT_DIFF_VERSION<>B.CNT_DIFF_INSTALMENT AND \n                    B.CNT_DIFF_DAYS_PAYMENT<> B.CNT_DIFF_DAYS_INSTALLMENT THEN A.DAYS_ENTRY_PAYMENT\n             WHEN B.CNT_DIFF_VERSION<>B.CNT_DIFF_INSTALMENT AND \n                    A.AMT_INSTALMENT*2=A.AMT_PAYMENT THEN A.DAYS_ENTRY_PAYMENT\n             ELSE A.NUM_INSTALMENT_VERSION END \n    ) A, \n    (\n    SELECT A.SK_ID_CURR, A.SK_ID_PREV, A.NUM_INSTALMENT_VERSION, A.NUM_INSTALMENT_NUMBER, \n           A.DAYS_INSTALMENT, A.DAYS_ENTRY_PAYMENT, SUM(A.AMT_PAYMENT) SUM_PAYMENT\n    FROM\n    installments_payments A, \n                            (\n                            SELECT SK_ID_CURR, SK_ID_PREV, NUM_INSTALMENT_NUMBER, \n                                COUNT(DISTINCT NUM_INSTALMENT_VERSION) CNT_DIFF_VERSION,\n                                COUNT( DISTINCT DAYS_INSTALMENT) CNT_DIFF_DAYS_INSTALLMENT, \n                                COUNT(DISTINCT DAYS_ENTRY_PAYMENT) CNT_DIFF_DAYS_PAYMENT, \n                                COUNT(DISTINCT AMT_INSTALMENT) CNT_DIFF_INSTALMENT,\n                                COUNT(DISTINCT AMT_PAYMENT) CNT_DIFF_PAYMENT\n                            FROM\n                            installments_payments\n                            GROUP BY\n                            SK_ID_CURR, SK_ID_PREV, NUM_INSTALMENT_NUMBER\n                            ) B\n    ON\n    A.SK_ID_PREV=B.SK_ID_PREV\n    AND\n    A.NUM_INSTALMENT_NUMBER=B.NUM_INSTALMENT_NUMBER\n    GROUP BY\n    A.SK_ID_CURR, A.SK_ID_PREV, A.NUM_INSTALMENT_NUMBER, \n        CASE WHEN B.CNT_DIFF_VERSION=B.CNT_DIFF_INSTALMENT AND \n                    B.CNT_DIFF_PAYMENT<>B.CNT_DIFF_INSTALMENT THEN A.NUM_INSTALMENT_VERSION\n             WHEN B.CNT_DIFF_VERSION<>B.CNT_DIFF_INSTALMENT AND \n                    A.AMT_INSTALMENT*2=A.AMT_PAYMENT THEN A.NUM_INSTALMENT_VERSION\n             ELSE A.DAYS_ENTRY_PAYMENT END\n                ) B\nON\nA.SK_ID_PREV=B.SK_ID_PREV\nAND\nA.NUM_INSTALMENT_NUMBER= B.NUM_INSTALMENT_NUMBER\nAND\nA.NUM_INSTALMENT_VERSION=B.NUM_INSTALMENT_VERSION\nORDER BY\nA.SK_ID_CURR, A.SK_ID_PREV, A.NUM_INSTALMENT_NUMBER, A.DAYS_ENTRY_PAYMENT')


# In[ ]:


get_ipython().run_cell_magic('sql', '', 'CREATE TABLE installments_payments_2 AS\nSELECT DISTINCT A.SK_ID_CURR, A.SK_ID_PREV, B.CNT_CREDIT,\n       B.CNT_INSTALMENT_NUMBER, B.CNT_DEFOULT_RECORD, \n       MEAN_DAYS_DISTINCT, MEAN_QUANTITY_DISTINCT, MIN_DAYS_DISTINCT, MAX_DAYS_DISTINCT,\n       B.CNT_LESS_PAYMENT_RECORD, B.MIN_QUANTITY_DISTINCT, B.MAX_QUANTITY_DISTINCT\nFROM\n(\nSELECT SK_ID_CURR, SK_ID_PREV,NUM_INSTALMENT_NUMBER,\n       DAYS_INSTALMENT-DAYS_ENTRY_PAYMENT DAY_DISTINCT, \n       SUM_INSTALLMENT-SUM_PAYMENT QUANTITY_DISTINCT,\n       CASE WHEN DAYS_INSTALMENT-DAYS_ENTRY_PAYMENT<0 THEN 1 ELSE 0 END DEFOULT_DAYS,\n       CASE WHEN SUM_INSTALLMENT-SUM_PAYMENT>1 THEN 1 ELSE 0 END LESS_PAYMENT\nFROM\ninstallments_payments_1\n) A,\n            (\n            SELECT SK_ID_CURR, COUNT(DISTINCT SK_ID_PREV) CNT_CREDIT, \n                    COUNT(NUM_INSTALMENT_NUMBER) CNT_INSTALMENT_NUMBER, SUM(DEFOULT_DAYS) CNT_DEFOULT_RECORD,\n                    AVG(DAY_DISTINCT) MEAN_DAYS_DISTINCT, AVG(QUANTITY_DISTINCT) MEAN_QUANTITY_DISTINCT, \n                    MIN(DAY_DISTINCT) MIN_DAYS_DISTINCT, MAX(DAY_DISTINCT) MAX_DAYS_DISTINCT,\n                    SUM(LESS_PAYMENT) CNT_LESS_PAYMENT_RECORD, MIN(QUANTITY_DISTINCT) MIN_QUANTITY_DISTINCT, \n                    MAX(QUANTITY_DISTINCT) MAX_QUANTITY_DISTINCT\n            FROM\n            (\n            SELECT SK_ID_CURR, SK_ID_PREV,NUM_INSTALMENT_NUMBER,\n                    DAYS_INSTALMENT-DAYS_ENTRY_PAYMENT DAY_DISTINCT, \n                    SUM_INSTALLMENT-SUM_PAYMENT QUANTITY_DISTINCT,\n                    CASE WHEN DAYS_INSTALMENT-DAYS_ENTRY_PAYMENT<0 THEN 1 ELSE 0 END DEFOULT_DAYS,\n                    CASE WHEN SUM_INSTALLMENT-SUM_PAYMENT>1 THEN 1 ELSE 0 END LESS_PAYMENT\n            FROM\n            installments_payments_1\n            ) \n            GROUP BY\n            SK_ID_CURR\n            ) B\nON\nA.SK_ID_CURR=B.SK_ID_CURR')


# In[ ]:


get_ipython().run_cell_magic('sql', '', 'CREATE TABLE installments_payments_3 AS\nSELECT DISTINCT A.SK_ID_CURR, A.CNT_CREDIT, \n       A.CNT_INSTALMENT_NUMBER, A.CNT_DEFOULT_RECORD, A.CNT_LESS_PAYMENT_RECORD,\n       A.MEAN_DAYS_DISTINCT, A.MEAN_QUANTITY_DISTINCT, A.MIN_DAYS_DISTINCT, A.MAX_DAYS_DISTINCT,\n       A.MIN_QUANTITY_DISTINCT, A.MAX_QUANTITY_DISTINCT,\n       CASE WHEN B.CNT_DEFOULT_CREDIT IS NULL THEN 0 ELSE B.CNT_DEFOULT_CREDIT END CNT_DEFOULT_CREDIT,\n       CASE WHEN C.CNT_LESS_PAYMENT_CREDIT IS NULL THEN 0 ELSE C.CNT_LESS_PAYMENT_CREDIT END CNT_LESS_PAYMENT_CREDIT,\n       B.CNT_DEFOULT_CREDIT*100/A.CNT_CREDIT RATIO_DEFOULT_CREDIT,\n       C.CNT_LESS_PAYMENT_CREDIT*100/A.CNT_CREDIT RATIO_LESS_PAYMENT_CREDIT,\n       A.CNT_DEFOULT_RECORD*100/A.CNT_INSTALMENT_NUMBER RATIO_DEFOULT_RECORD,\n       A.CNT_LESS_PAYMENT_RECORD*100/A.CNT_INSTALMENT_NUMBER RATIO_LESS_PAYMENT_RECORD\nFROM\ninstallments_payments_2 A LEFT JOIN \n    (\n     SELECT SK_ID_CURR, COUNT(DISTINCT SK_ID_PREV) CNT_DEFOULT_CREDIT\n     FROM\n     installments_payments_2\n     WHERE\n     CNT_DEFOULT_RECORD>0\n     GROUP BY\n     SK_ID_CURR\n    ) B LEFT JOIN\n       (\n     SELECT SK_ID_CURR, COUNT(DISTINCT SK_ID_PREV) CNT_LESS_PAYMENT_CREDIT\n     FROM\n     installments_payments_2\n     WHERE\n     CNT_LESS_PAYMENT_RECORD>0\n     GROUP BY\n     SK_ID_CURR\n    ) C\nON\nA.SK_ID_CURR=B.SK_ID_CURR\nAND\nB.SK_ID_CURR=C.SK_ID_CURR')
