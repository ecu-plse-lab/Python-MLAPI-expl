"""
This kernel provides a simple starter framework for a LightGBM model.

There are two supplementary functions designed with room to grow as the kernel develops:
    - feature_engineering: Contains the appending of extra features to the main dataset. There are
      a lot of datasets to go through in this challenge, so this is very much in progress
    - process_dataframe: Takes the engineered dataframe and makes it ready for LightGBM. Currently
      is only label encoding thanks to LightGBMs flexbility with nulls and not needing one-hots
"""
import os
import gc
import pandas as pd
import numpy as np
import lightgbm as lgbm
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

""" Load and process inputs """
input_dir = os.path.join(os.pardir, 'input/processed-input-data-after-aggregation-and-merge/')
print('Input files:\n{}'.format(os.listdir(input_dir)))
print('Loading data sets...')

sample_size = None
processdata_df = pd.read_csv(os.path.join(input_dir, 'processed_input_data.csv'), nrows=sample_size)
nobureau_df=processdata_df.filter(['AMT_ANNUITY',
'AMT_CREDIT',
'AMT_GOODS_PRICE',
'AMT_INCOME_TOTAL',
'AMT_REQ_CREDIT_BUREAU_DAY',
'AMT_REQ_CREDIT_BUREAU_HOUR',
'AMT_REQ_CREDIT_BUREAU_MON',
'AMT_REQ_CREDIT_BUREAU_QRT',
'AMT_REQ_CREDIT_BUREAU_WEEK',
'AMT_REQ_CREDIT_BUREAU_YEAR',
'APARTMENTS_AVG',
'APARTMENTS_MEDI',
'APARTMENTS_MODE',
'BASEMENTAREA_AVG',
'BASEMENTAREA_MEDI',
'BASEMENTAREA_MODE',
'CNT_CHILDREN',
'CNT_FAM_MEMBERS',
'CODE_GENDER',
'COMMONAREA_AVG',
'COMMONAREA_MEDI',
'COMMONAREA_MODE',
'DAYS_BIRTH',
'DAYS_EMPLOYED',
'DAYS_ID_PUBLISH',
'DAYS_LAST_PHONE_CHANGE',
'DAYS_REGISTRATION',
'DEF_30_CNT_SOCIAL_CIRCLE',
'DEF_60_CNT_SOCIAL_CIRCLE',
'ELEVATORS_AVG',
'ELEVATORS_MEDI',
'ELEVATORS_MODE',
'EMERGENCYSTATE_MODE',
'ENTRANCES_AVG',
'ENTRANCES_MEDI',
'ENTRANCES_MODE',
'EXT_SOURCE_1',
'EXT_SOURCE_2',
'EXT_SOURCE_3',
'FLAG_CONT_MOBILE',
'FLAG_DOCUMENT_10',
'FLAG_DOCUMENT_11',
'FLAG_DOCUMENT_12',
'FLAG_DOCUMENT_13',
'FLAG_DOCUMENT_14',
'FLAG_DOCUMENT_15',
'FLAG_DOCUMENT_16',
'FLAG_DOCUMENT_17',
'FLAG_DOCUMENT_18',
'FLAG_DOCUMENT_19',
'FLAG_DOCUMENT_2',
'FLAG_DOCUMENT_20',
'FLAG_DOCUMENT_21',
'FLAG_DOCUMENT_3',
'FLAG_DOCUMENT_4',
'FLAG_DOCUMENT_5',
'FLAG_DOCUMENT_6',
'FLAG_DOCUMENT_7',
'FLAG_DOCUMENT_8',
'FLAG_DOCUMENT_9',
'FLAG_EMAIL',
'FLAG_EMP_PHONE',
'FLAG_MOBIL',
'FLAG_OWN_CAR',
'FLAG_OWN_REALTY',
'FLAG_PHONE',
'FLAG_WORK_PHONE',
'FLOORSMAX_AVG',
'FLOORSMAX_MEDI',
'FLOORSMAX_MODE',
'FLOORSMIN_AVG',
'FLOORSMIN_MEDI',
'FLOORSMIN_MODE',
'FONDKAPREMONT_MODE',
'HOUR_APPR_PROCESS_START',
'HOUSETYPE_MODE',
'LANDAREA_AVG',
'LANDAREA_MEDI',
'LANDAREA_MODE',
'LIVE_CITY_NOT_WORK_CITY',
'LIVE_REGION_NOT_WORK_REGION',
'LIVINGAPARTMENTS_AVG',
'LIVINGAPARTMENTS_MEDI',
'LIVINGAPARTMENTS_MODE',
'LIVINGAREA_AVG',
'LIVINGAREA_MEDI',
'LIVINGAREA_MODE',
'NAME_CONTRACT_TYPE',
'NAME_EDUCATION_TYPE',
'NAME_FAMILY_STATUS',
'NAME_HOUSING_TYPE',
'NAME_INCOME_TYPE',
'NAME_TYPE_SUITE',
'NONLIVINGAPARTMENTS_AVG',
'NONLIVINGAPARTMENTS_MEDI',
'NONLIVINGAPARTMENTS_MODE',
'NONLIVINGAREA_AVG',
'NONLIVINGAREA_MEDI',
'NONLIVINGAREA_MODE',
'OBS_30_CNT_SOCIAL_CIRCLE',
'OBS_60_CNT_SOCIAL_CIRCLE',
'OCCUPATION_TYPE',
'ORGANIZATION_TYPE',
'OWN_CAR_AGE',
'REGION_POPULATION_RELATIVE',
'REGION_RATING_CLIENT',
'REGION_RATING_CLIENT_W_CITY',
'REG_CITY_NOT_LIVE_CITY',
'REG_CITY_NOT_WORK_CITY',
'REG_REGION_NOT_LIVE_REGION',
'REG_REGION_NOT_WORK_REGION',
'SK_ID_CURR',
'TARGET',
'TOTALAREA_MODE',
'WALLSMATERIAL_MODE',
'WEEKDAY_APPR_PROCESS_START',
'YEARS_BEGINEXPLUATATION_AVG',
'YEARS_BEGINEXPLUATATION_MEDI',
'YEARS_BEGINEXPLUATATION_MODE',
'YEARS_BUILD_AVG',
'YEARS_BUILD_MEDI',
'YEARS_BUILD_MODE',
'LOAN_INCOME_RATIO',
'ANNUITY_INCOME_RATIO',
'ANNUITY LENGTH',
'WORKING_LIFE_RATIO',
'INCOME_PER_FAM',
'CHILDREN_RATIO',
'MONTHS_BALANCE',
'DAYS_CREDIT',
'CREDIT_DAY_OVERDUE',
'DAYS_CREDIT_ENDDATE',
'DAYS_ENDDATE_FACT',
'AMT_CREDIT_MAX_OVERDUE',
'CNT_CREDIT_PROLONG',
'AMT_CREDIT_SUM',
'AMT_CREDIT_SUM_DEBT',
'AMT_CREDIT_SUM_LIMIT',
'AMT_CREDIT_SUM_OVERDUE',
'DAYS_CREDIT_UPDATE',
'AMT_ANNUITY_BMEAN',
'SK_ID_BUREAU_BMAX',
'CREDIT_ACTIVE',
'CREDIT_CURRENCY',
'DAYS_CREDIT_BMAX',
'CREDIT_DAY_OVERDUE_BMAX',
'DAYS_CREDIT_ENDDATE_BMAX',
'DAYS_ENDDATE_FACT_BMAX',
'AMT_CREDIT_MAX_OVERDUE_BMAX',
'CNT_CREDIT_PROLONG_BMAX',
'AMT_CREDIT_SUM_BMAX',
'AMT_CREDIT_SUM_DEBT_BMAX',
'AMT_CREDIT_SUM_LIMIT_BMAX',
'AMT_CREDIT_SUM_OVERDUE_BMAX',
'CREDIT_TYPE',
'DAYS_CREDIT_UPDATE_BMAX',
'AMT_ANNUITY_BMAX',
'SK_ID_BUREAU_BMIN',
'CREDIT_ACTIVE_BMIN',
'CREDIT_CURRENCY_BMIN',
'DAYS_CREDIT_BMIN',
'CREDIT_DAY_OVERDUE_BMIN',
'DAYS_CREDIT_ENDDATE_BMIN',
'DAYS_ENDDATE_FACT_BMIN',
'AMT_CREDIT_MAX_OVERDUE_BMIN',
'CNT_CREDIT_PROLONG_BMIN',
'AMT_CREDIT_SUM_BMIN',
'AMT_CREDIT_SUM_DEBT_BMIN',
'AMT_CREDIT_SUM_LIMIT_BMIN',
'AMT_CREDIT_SUM_OVERDUE_BMIN',
'CREDIT_TYPE_BMIN',
'DAYS_CREDIT_UPDATE_BMIN',
'AMT_ANNUITY_BMIN',
'MONTHS_BALANCE_B_B',
'STATUS'])
nobureau_df.to_csv('processed_input_bureau_only.csv', index = False)
print('Processed Input with only Bureau file is generated')