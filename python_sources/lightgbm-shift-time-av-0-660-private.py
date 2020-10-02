#This was my highest submission in the competition. A very early draft that shifts the time of the Test set to match the Train distribution. 

import pandas as pd
import numpy as np
import lightgbm as lgb
from scipy.sparse import vstack, csr_matrix, save_npz, load_npz
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import StratifiedKFold
#from sklearn.metrics import roc_auc_score
import gc
gc.enable()

dtypes = {
        'MachineIdentifier':                                    'category',
        'ProductName':                                          'category',
        'EngineVersion':                                        'category',
        'AppVersion':                                           'category',
        'AvSigVersion':                                         'category',
        'IsBeta':                                               'int8',
        'RtpStateBitfield':                                     'category',
        'IsSxsPassiveMode':                                     'int8',
        'DefaultBrowsersIdentifier':                            'float16',
        'AVProductStatesIdentifier':                            'category',
        'AVProductsInstalled':                                  'category',
        'AVProductsEnabled':                                    'float16',
        'HasTpm':                                               'int8',
        'CountryIdentifier':                                    'int16',
        'CityIdentifier':                                       'float32',
        'OrganizationIdentifier':                               'float16',
        'GeoNameIdentifier':                                    'float16',
        'LocaleEnglishNameIdentifier':                          'int8',
        'Platform':                                             'category',
        'Processor':                                            'category',
        'OsVer':                                                'category',
        'OsBuild':                                              'int16',
        'OsSuite':                                              'int16',
        'OsPlatformSubRelease':                                 'category',
        'OsBuildLab':                                           'category',
        'SkuEdition':                                           'category',
        'IsProtected':                                          'float16',
        'AutoSampleOptIn':                                      'int8',
        'PuaMode':                                              'category',
        'SMode':                                                'float16',
        'IeVerIdentifier':                                      'float16',
        'SmartScreen':                                          'category',
        'Firewall':                                             'float16',
        'UacLuaenable':                                         'category',
        'Census_MDC2FormFactor':                                'category',
        'Census_DeviceFamily':                                  'category',
        'Census_OEMNameIdentifier':                             'float16',
        'Census_OEMModelIdentifier':                            'float32',
        'Census_ProcessorCoreCount':                            'category',
        'Census_ProcessorManufacturerIdentifier':               'category',
        'Census_ProcessorModelIdentifier':                      'float16',
        'Census_ProcessorClass':                                'category',
        'Census_PrimaryDiskTotalCapacity':                      'float32',
        'Census_PrimaryDiskTypeName':                           'category',
        'Census_SystemVolumeTotalCapacity':                     'float32',
        'Census_HasOpticalDiskDrive':                           'int8',
        'Census_TotalPhysicalRAM':                              'float32',
        'Census_ChassisTypeName':                               'category',
        'Census_InternalPrimaryDiagonalDisplaySizeInInches':    'float16',
        'Census_InternalPrimaryDisplayResolutionHorizontal':    'float16',
        'Census_InternalPrimaryDisplayResolutionVertical':      'float16',
        'Census_PowerPlatformRoleName':                         'category',
        'Census_InternalBatteryType':                           'category',
        'Census_InternalBatteryNumberOfCharges':                'float32',
        'Census_OSVersion':                                     'category',
        'Census_OSArchitecture':                                'category',
        'Census_OSBranch':                                      'category',
        'Census_OSBuildNumber':                                 'int16',
        'Census_OSBuildRevision':                               'int32',
        'Census_OSEdition':                                     'category',
        'Census_OSSkuName':                                     'category',
        'Census_OSInstallTypeName':                             'category',
        'Census_OSInstallLanguageIdentifier':                   'float16',
        'Census_OSUILocaleIdentifier':                          'int16',
        'Census_OSWUAutoUpdateOptionsName':                     'category',
        'Census_IsPortableOperatingSystem':                     'int8',
        'Census_GenuineStateName':                              'category',
        'Census_ActivationChannel':                             'category',
        'Census_IsFlightingInternal':                           'float16',
        'Census_IsFlightsDisabled':                             'float16',
        'Census_FlightRing':                                    'category',
        'Census_ThresholdOptIn':                                'float16',
        'Census_FirmwareManufacturerIdentifier':                'float16',
        'Census_FirmwareVersionIdentifier':                     'float32',
        'Census_IsSecureBootEnabled':                           'int8',
        'Census_IsWIMBootEnabled':                              'float16',
        'Census_IsVirtualDevice':                               'float16',
        'Census_IsTouchEnabled':                                'int8',
        'Census_IsPenCapable':                                  'int8',
        'Census_IsAlwaysOnAlwaysConnectedCapable':              'float16',
        'Wdft_IsGamer':                                         'float16',
        'Wdft_RegionIdentifier':                                'float16',
        'HasDetections':                                        'int8'
        }

no_encoding = ['Census_OSWUAutoUpdateOptionsName', 'ProductName', 'Census_ActivationChannel', 
            'Census_PrimaryDiskTypeName', 'Platform', 'Census_ProcessorClass', 
            'Census_OSArchitecture', 'Processor', 'Census_DeviceFamily', 'PuaMode', 
            'Census_IsFlightingInternal', 'Census_ThresholdOptIn', 'Census_IsWIMBootEnabled', 
            'SMode', 'Wdft_IsGamer', 'Census_IsFlightsDisabled', 'Firewall', 
            'Census_IsAlwaysOnAlwaysConnectedCapable', 'IsProtected', 'Census_IsVirtualDevice', 
            'Census_IsSecureBootEnabled', 'AutoSampleOptIn', 'HasTpm', 'Census_IsPortableOperatingSystem', 
            'Census_IsPenCapable', 'Census_HasOpticalDiskDrive', 'IsSxsPassiveMode', 'IsBeta', 
            'Census_IsTouchEnabled', 'SkuEdition', 'OsPlatformSubRelease', 'Census_OSInstallTypeName', 
            'Census_PowerPlatformRoleName', 'Census_FlightRing', 'Census_MDC2FormFactor', 
            'Census_OSInstallLanguageIdentifier', 'AVProductsEnabled']

freq_unused = ['Census_OEMModelIdentifier', 'CityIdentifier', 'Census_FirmwareVersionIdentifier', 
            'Census_InternalBatteryNumberOfCharges', 'AVProductStatesIdentifier', 'Census_ProcessorModelIdentifier', 
            'Census_OEMNameIdentifier', 'DefaultBrowsersIdentifier', 'IeVerIdentifier', 'GeoNameIdentifier', 
            'LocaleEnglishNameIdentifier', 'CountryIdentifier', 'OrganizationIdentifier', 'Census_ChassisTypeName', 
            'OsSuite', 'Wdft_RegionIdentifier', 'Census_OSUILocaleIdentifier', 'Census_FirmwareManufacturerIdentifier', 
            'OsBuildLab', 'Census_OSVersion', 'Census_OSBuildRevision', 'Census_OSBuildNumber', 'OsBuild', 
            'OsVer', 'Census_InternalBatteryType', 'Census_OSSkuName', 'Census_OSBranch', 'Census_OSEdition']

factorize = ['Census_SystemVolumeTotalCapacity', 'Census_PrimaryDiskTotalCapacity', 'Census_TotalPhysicalRAM', 
            'Census_InternalPrimaryDisplayResolutionHorizontal', 'Census_InternalPrimaryDisplayResolutionVertical', 
            'Census_InternalPrimaryDiagonalDisplaySizeInInches']

manual_encondig = ['AVProductsInstalled', 'UacLuaenable', 'SmartScreen', 'Census_ProcessorCoreCount', 
            'Census_ProcessorManufacturerIdentifier', 'RtpStateBitfield', 'Census_GenuineStateName']

time_features = ['AvSigVersion', 'AppVersion', 'EngineVersion']

usecolums = no_encoding+freq_unused+factorize+manual_encondig+time_features

print('Download Train and Test Data.\n')
train = pd.read_csv('../input/train.csv', dtype=dtypes, low_memory=True) #usecols=usecolums+['HasDetections', 'MachineIdentifier'], 
train['MachineIdentifier'] = train.index.astype('uint32')
test  = pd.read_csv('../input/test.csv', dtype=dtypes, low_memory=True) #usecols=usecolums+['MachineIdentifier'], 
test['MachineIdentifier']  = test.index.astype('uint32')

gc.collect()

print("Frequency Encoding Features.\n")
def frequency_and_unused(df_train, df_test, feature, threshold=1000):
    print("Encoding Feature: ", feature)
    print("Set as category: ", feature)
    df_train[feature] = df_train[feature].astype('category')
    df_test[feature] = df_test[feature].astype('category')
    
    print("Look for differences: ", feature)
    trainvaluesnotintest = set(df_train[feature].unique()) - set(df_test[feature].unique())
    testvaluesnotintrain = set(df_test[feature].unique()) - set(df_train[feature].unique())

    print("Replace values not in Train/Test: ", feature)
    df_train.loc[df_train[feature].isin(trainvaluesnotintest), feature] = None
    df_test.loc[df_test[feature].isin(testvaluesnotintrain), feature] = None

    print("Remove unused categories: ", feature)
    df_train[feature] = df_train[feature].cat.remove_unused_categories()
    df_test[feature] = df_test[feature].cat.remove_unused_categories()

    print("Remove items less than or equal to threshold: ", feature)
    #threshold = 100  # Remove items less than or equal to threshold
    vc = df_train[feature].value_counts()
    vals_to_remove = vc[vc <= threshold].index.values
    df_train.loc[df_train[feature].isin(vals_to_remove), feature] = None
    vc = df_test[feature].value_counts()
    vals_to_remove = vc[vc <= threshold].index.values
    df_test.loc[df_test[feature].isin(vals_to_remove), feature] = None

    print("Look for differences: ", feature)
    trainvaluesnotintest = set(df_train[feature].unique()) - set(df_test[feature].unique())
    testvaluesnotintrain = set(df_test[feature].unique()) - set(df_train[feature].unique())

    print("Replace values not in Train/Test: ", feature)
    df_train.loc[df_train[feature].isin(trainvaluesnotintest), feature] = None
    df_test.loc[df_test[feature].isin(testvaluesnotintrain), feature] = None

    print("Remove unused categories: ", feature)
    df_train[feature] = df_train[feature].cat.remove_unused_categories()
    df_test[feature] = df_test[feature].cat.remove_unused_categories()

    gc.collect()

    return df_train, df_test

for feature in freq_unused:
    train, test = frequency_and_unused(train, test, feature=feature, threshold=1000)

gc.collect()

def numerical_encode(df_train, df_test, features, bins=200):
    for feature in features:
        print("Encoding Feature: ", feature)
        df_train = df_train.replace({feature: 
                                     {np.nan:'0'}})
        df_train[feature] = df_train[feature].astype('float32')
        df_train[feature] = pd.cut(df_train[feature].values, bins=bins, labels=False)

        df_test = df_test.replace({feature: 
                                     {np.nan:'0'}})
        df_test[feature] = df_test[feature].astype('float32')
        df_test[feature] = pd.cut(df_test[feature].values, bins=bins, labels=False)
    return df_train, df_test

bin_one = ['Census_SystemVolumeTotalCapacity', 'Census_PrimaryDiskTotalCapacity']
train, test = numerical_encode(train, test, features=bin_one, bins=[0, 16000, 256000, 512000, 1024000, 2048000, 999999999])

train, test = numerical_encode(train, test, features=['Census_TotalPhysicalRAM'], bins=[0, 1024, 4096, 8192, 16000, 32000, 64000, 999999999])

train, test = numerical_encode(train, test, features=['Census_InternalPrimaryDisplayResolutionVertical'], bins=[0, 480, 600, 768, 800, 900, 1024, 1080, 1440, 1800, 2160, 99999999])

train, test = numerical_encode(train, test, features=['Census_InternalPrimaryDisplayResolutionHorizontal'], bins=[0, 768, 800, 1024, 1080, 1280, 1366, 1440, 1600, 1680, 1920, 2160, 2560, 3200, 99999999])

train, test = numerical_encode(train, test, features=['Census_InternalPrimaryDiagonalDisplaySizeInInches'], bins=[0, 10, 11, 13, 14, 15, 16, 18, 20, 22, 23, 24, 27, 30, 50, 70, 999999999])

gc.collect()


print("Time Encoding Features")

for feature in time_features:
    #Convolute Version Numbers
    if feature == 'EngineVersion':
        print("Time Encoding Feature: ", feature)
        version_number = []
        for line in train['EngineVersion']:
            col = line.split('.')  #gives third colum value of version number 1.1."2133".3
            if int(col[2]) <= 12800: col[2] = 12800  #bin all really old version
            if int(col[2]) == 15300: col[2] = 15400
            col[2] = int(round(int(col[2])/100))
            version_number.append(int(col[2])+2) #shift training data to match test data
        train['EngineVersion'] = version_number
        version_number = []
        for line in test['EngineVersion']:
            col = line.split('.')  #gives second colum value of version number 1."273".2133.3
            if int(col[2]) <= 13000: col[2] = 13000  #bin all really old version
            col[2] = int(round(int(col[2])/100))
            version_number.append(col[2])
        test['EngineVersion'] = version_number #now in range 120 - 155
        del col
        gc.collect()
        
    #Convolute Version Numbers
    if feature == 'AppVersion':
        print("Time Encoding Feature: ", feature)
        version_number = []
        for line in train['AppVersion']:
            #print(line)
            col = line.split('.')  #gives second colum value of version number 1."273".2133.3
            version_number.append(int(col[1]))
        train['AppVersion'] = version_number
        version_number = []
        for line in test['AppVersion']:
            col = line.split('.')  #gives second colum value of version number 1."273".2133.3
            version_number.append(int(col[1]))
        test['AppVersion'] = version_number #now in range 4 - 18
        del col
        gc.collect()

    #Convolute Version Numbers
    if feature == 'AvSigVersion':
        print("Time Encoding Feature: ", feature)
        version_number = []
        for line in train['AvSigVersion']:
            #print(line)
            #print(version.parse(str(line)))
            col = line.split('.')  #gives second colum value of version number 1."273".2133.3
            if str(col[1]) == '2&#x17;3': col[1] = 217 #data correction
            if int(col[1]) == 0: col[1] = 275  #fault value mapped to most common value
            if int(col[1]) <= 216: col[1] = 216  #bin all really old version
            version_number.append(int(col[1])+4) #shift training data to match test data
        train['AvSigVersion'] = version_number
        version_number = []
        for line in test['AvSigVersion']:
            #print(line)
            #print(version.parse(str(line)))
            col = line.split('.')  #gives second colum value of version number 1."273".2133.3
            if int(col[1]) == 0: col[1] = 277  #fault value mapped to most common value
            if int(col[1]) <= 220: col[1] = 220  #bin all really old version
            version_number.append(int(col[1]))
        test['AvSigVersion'] = version_number
        del col
        gc.collect()

gc.collect()

#Encode AVProductsInstalled
print("Hand encoding AVProductsInstalled")
train = train.replace({'AVProductsInstalled': 
                             {np.nan:None,
                              '5':'4',
                              '6':'4',
                              '7':'4',
                              '0':None
                             }})
        
test = test.replace({'AVProductsInstalled': 
                             {np.nan:None,
                              '5':'4',
                              '6':'4',
                              '7':'4',
                              '0':None
                             }})
print("Hand encoding AVProductsInstalled -- done")

gc.collect()

#Encode UacLuaenable
print("Hand encoding UacLuaenable")
train = train.replace({'UacLuaenable': 
                             {np.nan:None,
                              '0':None,
                              '2':None,
                              '3':None,
                              '16777216':None,
                              '6357062':None,
                              '5':None,
                              '7798884':None,
                              '48':None,
                              '49':None,
                              '255':None
                             }})
test = test.replace({'UacLuaenable': 
                             {np.nan:None,
                              '0':None,
                              '2':None,
                              '3':None,
                              '5':None,
                              '6357062':None,
                              '808482880':None,
                              '537591872':None,
                              '537591856':None,
                              '808482864':None,
                              '48':None,
                              '49':None
                             }})
print("Hand encoding UacLuaenable -- done")

gc.collect()


#Encode RtpStateBitfield
print("Hand encoding RtpStateBitfield")
train = train.replace({'RtpStateBitfield': 
                             {np.nan:None,
                              '3':None,
                              '1':None,
                              '35':None,
                              '40':None
                             }})
test = test.replace({'RtpStateBitfield': 
                             {np.nan:None,
                              '3':None,
                              '1':None,
                              '35':None,
                              '40':None
                             }})
print("Hand encoding RtpStateBitfield -- done")

gc.collect()


#Encode Census_GenuineStateName
print("Hand encoding Census_GenuineStateName")
train = train.replace({'Census_GenuineStateName': 
                             {np.nan:None,
                              'UNKNOWN':None,
                              'TAMPERED':None
                             }})
test = test.replace({'Census_GenuineStateName': 
                             {np.nan:None,
                              'UNKNOWN':None,
                              'TAMPERED':None
                             }})
print("Hand encoding Census_GenuineStateName -- done")

gc.collect()


#Encode SmartScreen
print("Hand encoding SmartScreen")
train = train.replace({'SmartScreen': 
                         {np.nan:None,
                          '&#x01;':None,
                          '&#x02;':None,
                          '&#x03;':None,
                          'Deny':None,
                          '0':None,
                          '00000000':None,
                          'on':'On',
                          'Enabled':'On',
                          'requireadmin':'RequireAdmin',
                          'requireAdmin':'RequireAdmin',
                          'RequiredAdmin':'RequireAdmin',
                          'off':'Off',
                          'OFF':'Off',
                          'of':'Off',
                          'Promt':'Prompt',
                          'prompt':'Prompt',
                          'Promprt':'Prompt',
                          'warn':'Warn',
                          'BLOCK':'Block'
                         }})
test = test.replace({'SmartScreen':
                         {np.nan:None,
                          '&#x01;':None,
                          '&#x02;':None,
                          '&#x03;':None,
                          'Deny':None,
                          '0':None,
                          '00000000':None,
                          'on':'On',
                          'ON':'On',
                          'Enabled':'On',
                          'requireadmin':'RequireAdmin',
                          'requireAdmin':'RequireAdmin',
                          'RequiredAdmin':'RequireAdmin',
                          'off':'Off',
                          'OFF':'Off',
                          'of':'Off',
                          'Promt':'Prompt',
                          'prompt':'Prompt',
                          'Promprt':'Prompt',
                          'warn':'Warn',
                          'BLOCK':'Block'
                         }})
print("Hand encoding SmartScreen -- done")


gc.collect()

#Encode Census_ProcessorManufacturerIdentifier
print("Hand encoding Census_ProcessorManufacturerIdentifier")
train = train.replace({'Census_ProcessorManufacturerIdentifier': 
                         {np.nan:None,
                          '2':None,
                          '3':None,
                          '4':None,
                          '5':None,
                          '6':None,
                          '7':None,
                          '8':None,
                          '9':None,
                          '10':None
                         }})
test = test.replace({'Census_ProcessorManufacturerIdentifier': 
                         {np.nan:None,
                          '2':None,
                          '3':None,
                          '4':None,
                          '5':None,
                          '6':None,
                          '7':None,
                          '8':None,
                          '9':None,
                          '10':None
                         }})
print("Hand encoding Census_ProcessorManufacturerIdentifier -- done")


gc.collect()

#Encode Census_ProcessorCoreCount
print("Hand encoding Census_ProcessorCoreCount")
train = train.replace({'Census_ProcessorCoreCount': 
                             {np.nan:None,
                              '5':'6',
                              '7':'6',
                              '9':'12',
                              '10':'12',
                              '11':'12',
                              '13':'12',
                              '14':'12',
                              '15':'16',
                              '17':'16',
                              '18':'16',
                              '32':'16',
                              '24':'16',
                              '20':'16',
                              '40':'16',
                              '36':'16',
                              '28':'16',
                              '48':'16',
                              '56':'16',
                              '64':'16',
                              '72':'16',
                              '88':'16',
                              '80':'16',
                              '44':'16',
                              '30':'16',
                              '96':'16',
                              '112':'16',
                              '22':'16',
                              '46':'16',
                              '52':'16',
                              '128':'16',
                              '104':'16',
                              '26':'16',
                              '50':'16',
                              '54':'16',
                              '144':'16',
                              '120':'16',
                              '192':'16',
                              '25':'16'
                             }})
test = test.replace({'Census_ProcessorCoreCount': 
                             {np.nan:None,
                              '5':'6',
                              '7':'6',
                              '9':'12',
                              '10':'12',
                              '11':'12',
                              '13':'12',
                              '14':'12',
                              '15':'16',
                              '17':'16',
                              '18':'16',
                              '32':'16',
                              '24':'16',
                              '20':'16',
                              '40':'16',
                              '36':'16',
                              '28':'16',
                              '48':'16',
                              '56':'16',
                              '64':'16',
                              '72':'16',
                              '88':'16',
                              '80':'16',
                              '44':'16',
                              '30':'16',
                              '96':'16',
                              '112':'16',
                              '22':'16',
                              '46':'16',
                              '52':'16',
                              '128':'16',
                              '104':'16',
                              '26':'16',
                              '50':'16',
                              '54':'16',
                              '144':'16',
                              '120':'16',
                              '192':'16',
                              '25':'16',
                              '23':'16',
                              '224':'16',
                              '19':'16',
                              '35':'16'
                             }})
print("Hand encoding Census_ProcessorCoreCount -- done")

gc.collect()

print("List all values that are not in both sets:")
for feature in usecolums:
    trainvaluesnotintest = set(train[feature].unique()) - set(test[feature].unique())
    print(feature, ": Not in TEST: ", trainvaluesnotintest)
    testvaluesnotintest = set(test[feature].unique()) - set(train[feature].unique())
    print(feature, ": Not in TRAIN: ", testvaluesnotintest)
    del trainvaluesnotintest, testvaluesnotintest
print("List all values that are not in both sets --- END")

gc.collect()

print('Transform all features to category.\n')
for usecol in train.columns.tolist()[1:-1]:
    print("Transforming: ", usecol)
    train[usecol] = train[usecol].astype('str')
    test[usecol] = test[usecol].astype('str')
    
    #Fit LabelEncoder
    le = LabelEncoder().fit(
            np.unique(train[usecol].unique().tolist()+
                      test[usecol].unique().tolist()))

    #At the end 0 will be used for dropped values
    train[usecol] = le.transform(train[usecol])+1
    test[usecol]  = le.transform(test[usecol])+1

    agg_tr = (train
              .groupby([usecol])
              .aggregate({'MachineIdentifier':'count'})
              .reset_index()
              .rename({'MachineIdentifier':'Train'}, axis=1))
    agg_te = (test
              .groupby([usecol])
              .aggregate({'MachineIdentifier':'count'})
              .reset_index()
              .rename({'MachineIdentifier':'Test'}, axis=1))

    agg = pd.merge(agg_tr, agg_te, on=usecol, how='outer').replace(np.nan, 0)
    #Select values with more than 1000 observations
    agg = agg[(agg['Train'] > 1000)].reset_index(drop=True)
    agg['Total'] = agg['Train'] + agg['Test']
    #Drop unbalanced values
    agg = agg[(agg['Train'] / agg['Total'] > 0.2) & (agg['Train'] / agg['Total'] < 0.8)]
    agg[usecol+'Copy'] = agg[usecol]

    train[usecol] = (pd.merge(train[[usecol]], 
                              agg[[usecol, usecol+'Copy']], 
                              on=usecol, how='left')[usecol+'Copy']
                     .replace(np.nan, 0).astype('int').astype('category'))

    test[usecol]  = (pd.merge(test[[usecol]], 
                              agg[[usecol, usecol+'Copy']], 
                              on=usecol, how='left')[usecol+'Copy']
                     .replace(np.nan, 0).astype('int').astype('category'))

    del le, agg_tr, agg_te, agg, usecol
    gc.collect()
          
y_train = np.array(train['HasDetections'])
train_ids = train.index
test_ids  = test.index

del train['HasDetections'], train['MachineIdentifier'], test['MachineIdentifier']
gc.collect()


print("List all values that are not in both sets:")
for feature in usecolums:
    trainvaluesnotintest = set(train[feature].unique()) - set(test[feature].unique())
    print(feature, ": Not in TEST: ", trainvaluesnotintest)
    testvaluesnotintest = set(test[feature].unique()) - set(train[feature].unique())
    print(feature, ": Not in TRAIN: ", testvaluesnotintest)
    del trainvaluesnotintest, testvaluesnotintest
print("List all values that are not in both sets --- END")



print("If you don't want use Sparse Matrix choose Kernel Version 2 to get simple solution.\n")

print('--------------------------------------------------------------------------------------------------------')
print('Transform Data to Sparse Matrix.')
print('Sparse Matrix can be used to fit a lot of models, eg. XGBoost, LightGBM, Random Forest, K-Means and etc.')
print('To concatenate Sparse Matrices by column use hstack()')
print('Read more about Sparse Matrix https://docs.scipy.org/doc/scipy/reference/sparse.html')
print('Good Luck!')
print('--------------------------------------------------------------------------------------------------------')

#Fit OneHotEncoder
ohe = OneHotEncoder(categories='auto', sparse=True, dtype='uint8').fit(train)

#Transform data using small groups to reduce memory usage
m = 100000

train = vstack([ohe.transform(train[i*m:(i+1)*m]) for i in range(train.shape[0] // m + 1)])
test  = vstack([ohe.transform(test[i*m:(i+1)*m])  for i in range(test.shape[0] // m +  1)])
save_npz('train.npz', train, compressed=True)
save_npz('test.npz',  test,  compressed=True)

del ohe, train, test
gc.collect()

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
skf.get_n_splits(train_ids, y_train)

lgb_test_result  = np.zeros(test_ids.shape[0])
lgb_train_result = np.zeros(train_ids.shape[0])

counter = 0

print('\nLightGBM\n')

for train_index, test_index in skf.split(train_ids, y_train):
    
    print('Fold {}\n'.format(counter + 1))
    
    train = load_npz('train.npz')
    X_fit = vstack([train[train_index[i*m:(i+1)*m]] for i in range(train_index.shape[0] // m + 1)])
    X_val = vstack([train[test_index[i*m:(i+1)*m]]  for i in range(test_index.shape[0] //  m + 1)])
    X_fit, X_val = csr_matrix(X_fit, dtype='float32'), csr_matrix(X_val, dtype='float32')
    y_fit, y_val = y_train[train_index], y_train[test_index]
    
    del train
    gc.collect()

    lgb_model = lgb.LGBMClassifier(max_depth=-1,
                                   n_estimators=30000,
                                   learning_rate=0.05,
                                   num_leaves=2**12-1,
                                   colsample_bytree=0.28,
                                   objective='binary', 
                                   n_jobs=-1)
                               
    lgb_model.fit(X_fit, y_fit, eval_metric='auc', 
                  eval_set=[(X_val, y_val)], 
                  verbose=100, early_stopping_rounds=100)
    
    del X_fit, X_val, y_fit, y_val, train_index, test_index
    gc.collect()
    
    test = load_npz('test.npz')
    test = csr_matrix(test, dtype='float32')
    lgb_test_result += lgb_model.predict_proba(test)[:,1]
    counter += 1
    
    del test
    gc.collect()
    
    #Stop fitting to prevent time limit error
    if counter == 1 : break

submission = pd.read_csv('../input/sample_submission.csv')
submission['HasDetections'] = lgb_test_result / counter
submission.to_csv('lgb_submission.csv', index=False)

print('\nDone.')