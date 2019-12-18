#################################################
# title   : housing prices: advanced regression techniques
# from    : kaggle.com
# file    : eval_preds.py
#         : philip walsh
#         : philipwalsh.ds@gmail.com
#         : 2019-12-18


import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

from os.path import isfile, join
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
import lightgbm as lgbm
from sklearn.metrics import mean_squared_error

bVerbose = False


my_test_size=0.1    # when ready to make the final sub
my_test_size=0.20   # normal training eval

working_dir=os.getcwd()
excluded_dir = os.path.join(working_dir, 'excluded') # working_dir + '\excluded'

print('\n\n')
print('*****')
print('***** start of script: eval_preds.py')
print('*****')
print('\n\n')

if bVerbose:
    print('\nworking dir   :', working_dir)



#print('saving X_sub ...', sendtofile(excluded_dir,'submisison_data(cleaned).csv',X_sub))
def sendtofile(outdir, filename, df, verbose=False):
    script_name='eval_preds_'
    out_file = os.path.join(outdir, script_name + filename)
    if verbose:
        print("saving file :", out_file)
    df.to_csv(out_file, index=False)
    return out_file


def get_decade(in_val):
    return int(in_val / 10) * 10

def CleanData(clean_me_df):

    # get rid of the Id column
    clean_me_df.drop('Id', axis=1, inplace=True)

    clean_me_df["IsRegularLotShape"] = (clean_me_df.LotShape == "Reg") * 1
    clean_me_df["IsLandLevel"] = (clean_me_df.LandContour == "Lvl") * 1
    clean_me_df["IsLandSlopeGntl"] = (clean_me_df.LandSlope == "Gtl") * 1
    clean_me_df["IsElectricalSBrkr"] = (clean_me_df.Electrical == "SBrkr") * 1
    clean_me_df["IsGarageDetached"] = (clean_me_df.GarageType == "Detchd") * 1
    clean_me_df["IsPavedDrive"] = (clean_me_df.PavedDrive == "Y") * 1
    clean_me_df["HasShed"] = (clean_me_df.MiscFeature == "Shed") * 1


    clean_me_df.loc[clean_me_df.Neighborhood == 'NridgHt', "Neighborhood_Good"] = 1
    clean_me_df.loc[clean_me_df.Neighborhood == 'Crawfor', "Neighborhood_Good"] = 1
    clean_me_df.loc[clean_me_df.Neighborhood == 'StoneBr', "Neighborhood_Good"] = 1
    clean_me_df.loc[clean_me_df.Neighborhood == 'Somerst', "Neighborhood_Good"] = 1
    clean_me_df.loc[clean_me_df.Neighborhood == 'NoRidge', "Neighborhood_Good"] = 1
    clean_me_df["Neighborhood_Good"].fillna(0, inplace=True)

    x=['PoolQC','MiscFeature','Alley','Fence']
    for n in x:
        clean_me_df.drop(n,axis=1, inplace=True)


    clean_me_df['ExterQual'].fillna('TA', inplace=True)

    clean_me_df['FireplaceQu'].fillna('NA', inplace=True)
    
    LotFrontage_mean = 0
    LotFrontage_mean = clean_me_df['LotFrontage'].mean()
    clean_me_df['LotFrontage'].fillna(LotFrontage_mean, inplace=True)


    clean_me_df['GarageCond'].fillna('TA', inplace=True)
    temp_mean = clean_me_df['GarageYrBlt'].mean()
    clean_me_df['GarageYrBlt'].fillna(temp_mean, inplace=True)
    clean_me_df['GarageFinish'].fillna('NA', inplace=True)    
    clean_me_df['GarageQual'].fillna('NA', inplace=True)    
    clean_me_df['GarageType'].fillna('NA', inplace=True)    
    clean_me_df['BsmtCond'].fillna('NA', inplace=True)    
    clean_me_df['BsmtExposure'].fillna('NA', inplace=True)    
    clean_me_df['BsmtQual'].fillna('NA', inplace=True)    
    clean_me_df['BsmtFinType2'].fillna('NA', inplace=True)    
    clean_me_df['BsmtFinType1'].fillna('NA', inplace=True)    
    clean_me_df['MasVnrType'].fillna('None', inplace=True)    
    clean_me_df['MasVnrArea'].fillna(0, inplace=True)
    
    clean_me_df['MSZoning'].fillna('RL', inplace=True)
    clean_me_df['Utilities'].fillna('AllPub', inplace=True)
    clean_me_df['BsmtHalfBath'].fillna(0, inplace=True)
    clean_me_df['BsmtFullBath'].fillna(0, inplace=True)
    clean_me_df['Functional'].fillna('Mod', inplace=True)
    clean_me_df['Exterior1st'].fillna('Plywood', inplace=True)
    clean_me_df['TotalBsmtSF'].fillna(0, inplace=True)
    clean_me_df['BsmtUnfSF'].fillna(0, inplace=True)
    clean_me_df['BsmtFinSF2'].fillna(0, inplace=True)
    clean_me_df['GarageArea'].fillna(0, inplace=True)
    clean_me_df['KitchenQual'].fillna('TA', inplace=True)
    clean_me_df['GarageCars'].fillna(0, inplace=True)
    clean_me_df['BsmtFinSF1'].fillna(0, inplace=True)
    clean_me_df['Exterior2nd'].fillna('Plywood', inplace=True)
    clean_me_df['SaleType'].fillna('Oth', inplace=True)
    clean_me_df['Electrical'].fillna('FuseA', inplace=True)
    

    # this didnt show up earlier as having NaN data, but out of an abundance of cauthion, make sure
    GrvLivArea_mean = 0
    GrvLivArea_mean = clean_me_df['GrLivArea'].mean()
    clean_me_df['GrLivArea'].fillna(GrvLivArea_mean, inplace=True)
    
    

    ## engineer a features
    
    #house age
    YearBullt_mean=0
    YearBullt_mean = clean_me_df['YearBuilt'].mean()
    clean_me_df['YearBuilt'].fillna(YearBullt_mean, inplace=True)    
    max_age = clean_me_df['YearBuilt'].max()
    clean_me_df['HouseAge'] = 1/((max_age+1)-clean_me_df['YearBuilt'])
    clean_me_df.drop('YearBuilt', axis=1, inplace=True)

    #RemodelAge
    YearRemodAdd_mean=0
    YearRemodAdd_mean = clean_me_df['YearRemodAdd'].mean()
    clean_me_df['YearRemodAdd'].fillna(YearRemodAdd_mean, inplace=True)    
    max_age = clean_me_df['YearRemodAdd'].max()
    clean_me_df['RemodelAge'] = 1/((max_age+1)-clean_me_df['YearRemodAdd'])
    clean_me_df['NewRemodel'] = (clean_me_df['YearRemodAdd']==clean_me_df['YrSold']) * 1
    clean_me_df.drop('YearRemodAdd', axis=1, inplace=True)
    
    #garageAge
    GarageYrBlt_mean=0
    GarageYrBlt_mean = clean_me_df['GarageYrBlt'].mean()
    clean_me_df['GarageYrBlt'].fillna(GarageYrBlt_mean, inplace=True)    
    max_age = clean_me_df['GarageYrBlt'].max()
    clean_me_df['GarageAge'] = 1/((max_age+1)-clean_me_df['GarageYrBlt'])    

    #NewGarage
    clean_me_df['NewGarage'] = (clean_me_df['GarageYrBlt']==clean_me_df['YrSold']) * 1
    clean_me_df.drop('GarageYrBlt', axis=1, inplace=True)    


    #one hot encode these, the rest can be categorized
    x=['MSSubClass','MSZoning','Street','LotShape','LandContour','LotConfig','LandSlope','Neighborhood','BldgType','HouseStyle','RoofStyle','RoofMatl','Exterior1st','Exterior2nd','MasVnrType','Foundation','Heating','GarageType','SaleType', 'SaleCondition']
    for n in x:
        df1 = pd.get_dummies(clean_me_df[n], prefix = n)
        clean_me_df = pd.concat([clean_me_df,df1], axis=1)

    # drop the columns that have been encoded
    for n in x:
        clean_me_df.drop(n,axis=1, inplace=True)


    #categorizing
    x = clean_me_df.select_dtypes(include=np.object).columns.tolist()
    for n in x:
        clean_me_df[n] = clean_me_df[n].astype('category')


    # a bunch of the categoricals have the same values
    # so we can just loop through them and deal with them almost in bulk
    x = ['ExterQual', 'ExterCond', 'BsmtQual', 'BsmtCond', 'HeatingQC', 'KitchenQual', 'FireplaceQu', 'GarageQual', 'GarageCond']
    
    # want numbers here, insted of text
    for n in x:
        clean_me_df[n] = clean_me_df[n].replace(dict(Ex=5, Gd=4, TA=3, Fa=2, NA=1, Po=0))
    
    #LightGBM does not like categorical so i turn them to int, and give them a new name
    for n in x:
        clean_me_df[n + '_INT'] = clean_me_df[n].astype('int')

    # then i drop the original
    for n in x:
        clean_me_df.drop(n, axis=1, inplace=True)
    

    # create a feature that adds up all the Quality and Condition vars
    clean_me_df['Total_Qual_Cond'] = (clean_me_df['ExterQual_INT']+clean_me_df['ExterCond_INT']+clean_me_df['BsmtQual_INT']+clean_me_df['BsmtCond_INT']+clean_me_df['HeatingQC_INT']+clean_me_df['KitchenQual_INT']+clean_me_df['FireplaceQu_INT']+clean_me_df['GarageQual_INT']+clean_me_df['GarageCond_INT'])

    # drop the original quality and condition vars
    x = ['ExterQual_INT', 'ExterCond_INT', 'BsmtQual_INT', 'BsmtCond_INT', 'HeatingQC_INT', 'KitchenQual_INT', 'FireplaceQu_INT', 'GarageQual_INT', 'GarageCond_INT']
    for n in x:
        clean_me_df.drop(n, axis=1, inplace=True)

    # handle the one off categoricals that have their own unique values
    # byt replacing text keys with numbers, making an INT col and drop the categorical
    #Utilities
    clean_me_df['Utilities'] = clean_me_df['Utilities'].replace(dict(AllPub=3,NoSewr=2, NoSeWa=1, ELO=0))
    clean_me_df['Utilities_INT'] = clean_me_df['Utilities'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('Utilities', axis=1, inplace=True)
    
    #Condition1
    clean_me_df['Condition1'] = clean_me_df['Condition1'].replace(dict(Artery=5, Feedr=4, Norm=3, RRNn=0, RRAn=0, PosN=3, PosA=2, RRNe=0, RRAe=0))
    clean_me_df['Condition1_INT'] = clean_me_df['Condition1'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('Condition1', axis=1, inplace=True)
    
    #Condition2
    clean_me_df['Condition2'] = clean_me_df['Condition2'].replace(dict(Artery=5, Feedr=4, Norm=3, RRNn=0, RRAn=0, PosN=3, PosA=2, RRNe=0, RRAe=0))
    clean_me_df['Condition2_INT'] = clean_me_df['Condition2'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('Condition2', axis=1, inplace=True)
    
    # BsmtExposure
    clean_me_df['BsmtExposure'] = clean_me_df['BsmtExposure'].replace(dict(Gd=3, Av=2, Mn=1, No=0, NA=0))
    clean_me_df['BsmtExposure_INT'] = clean_me_df['BsmtExposure'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('BsmtExposure', axis=1, inplace=True)
    
    # BsmtFinType1
    clean_me_df['BsmtFinType1'] = clean_me_df['BsmtFinType1'].replace(dict(GLQ=5, ALQ=4, BLQ=3, Rec=2, LwQ=1, Unf=0, NA=0))
    clean_me_df['BsmtFinType1_INT'] = clean_me_df['BsmtFinType1'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('BsmtFinType1', axis=1, inplace=True)
    
    # BsmtFinType2
    clean_me_df['BsmtFinType2'] = clean_me_df['BsmtFinType2'].replace(dict(GLQ=5, ALQ=4, BLQ=3, Rec=2, LwQ=1, Unf=0, NA=0))
    clean_me_df['BsmtFinType2_INT'] = clean_me_df['BsmtFinType2'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('BsmtFinType2', axis=1, inplace=True)
    
    # CentralAir
    clean_me_df['CentralAir'] = clean_me_df['CentralAir'].replace(dict(Y=1, N=0))
    clean_me_df['CentralAir_INT'] = clean_me_df['CentralAir'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('CentralAir', axis=1, inplace=True)
    
    # Electrical
    clean_me_df['Electrical'] = clean_me_df['Electrical'].replace(dict(SBrkr=4,FuseA=3, FuseF=2, FuseP=1, Mix=0))
    clean_me_df['Electrical_INT'] = clean_me_df['Electrical'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('Electrical', axis=1, inplace=True)
    
    # Functional
    clean_me_df['Functional'] = clean_me_df['Functional'].replace(dict(Typ=6, Min1=4, Min2=4, Mod=3, Maj1=2, Maj2=2, Sev=1, Sal=0))
    clean_me_df['Functional_INT'] = clean_me_df['Functional'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('Functional', axis=1, inplace=True)

    # GarageFinish
    clean_me_df['GarageFinish'] = clean_me_df['GarageFinish'].replace(dict(Fin=2, RFn=1, Unf=0, NA=0))
    clean_me_df['GarageFinish_INT'] = clean_me_df['GarageFinish'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('GarageFinish', axis=1, inplace=True)
    
    # PavedDrive
    clean_me_df['PavedDrive'] = clean_me_df['PavedDrive'].replace(dict(Y=2, P=1, N=0))
    clean_me_df['PavedDrive_INT'] = clean_me_df['PavedDrive'].astype('int')     #LightGBM does not like categorical so i turn them to int
    clean_me_df.drop('PavedDrive', axis=1, inplace=True)


    #count the bathrooms, then drop the original vars
    clean_me_df['BathroomCount'] =  clean_me_df['BsmtFullBath'] + (clean_me_df['BsmtHalfBath'] * .5) + clean_me_df['FullBath'] + (clean_me_df['HalfBath'] * .5)
    clean_me_df.drop('BsmtFullBath',axis=1, inplace=True)
    clean_me_df.drop('BsmtHalfBath',axis=1, inplace=True)
    clean_me_df.drop('FullBath',axis=1, inplace=True)
    clean_me_df.drop('HalfBath',axis=1, inplace=True)

    # if any column has more than 99.94 % zeros, drop it like its hot
    overfit = []
    for i in clean_me_df.columns:
        counts = clean_me_df[i].value_counts()
        zeros = counts.iloc[0]
        if zeros / len(clean_me_df) * 100 > 99.94:
            overfit.append(i)
    overfit = list(overfit)
    clean_me_df = clean_me_df.drop(overfit, axis=1).copy()

    # done with this function

    return clean_me_df




##
## MAIN SCRIPT START HERE
##

# load the data
train_data = pd.read_csv('excluded/train_full.csv', low_memory=False)
sub_data = pd.read_csv('excluded/test_full.csv', low_memory=False)


# find the outliers
if False:
    fig, axes = plt.subplots(ncols=5, nrows=2, figsize=(16, 4))
    axes = np.ravel(axes)
    col_name = ['GrLivArea','TotalBsmtSF','1stFlrSF','BsmtFinSF1','LotArea']
    for i, c in zip(range(5), col_name):
        train_data.plot.scatter(ax=axes[i], x=c, y='SalePrice', sharey=True, colorbar=False, c='r')

    plt.show()
    print(1/0)


train_data = train_data[train_data['GrLivArea'] < 4000]
train_data = train_data[train_data['LotArea'] < 100000]
train_data = train_data[train_data['TotalBsmtSF'] < 3000]
train_data = train_data[train_data['1stFlrSF'] < 2500]
train_data = train_data[train_data['BsmtFinSF1'] < 2000]


train_data = x1.copy()
# stratified shuffle split
# basically stratify the data by Gross Living Area
# get the test and hold-out data to jive with each other, regarding sampling based on these bins
# only useful in the linear model, the boosted/bagged treee based models should do fine with whatever we give them
train_data['living_area_cat'] = pd.cut(
    train_data['GrLivArea'], 
    bins=[0, 500, 1000, 1500, 2000, 2500, np.inf], 
    labels=[1, 2, 3, 4, 5, 6])



split = StratifiedShuffleSplit(n_splits=1, test_size=my_test_size, random_state=9261774)
for train_index, test_index in split.split(train_data, train_data['living_area_cat']):
    X_train = train_data.loc[train_index] # this is the training data
    X_test = train_data.loc[test_index]   # this is the hold out, the protion of the training i will use for testing

# set up the y aka the label
y_train = X_train['SalePrice']
y_test = X_test['SalePrice']

# drop SalePrice from the x vars
X_train.drop('SalePrice', axis=1, inplace=True)
X_test.drop('SalePrice', axis=1, inplace=True)


submission_id = sub_data['Id']  # this is the start of the submission data frame.  
                                # sub data is already loaded, store the Id now, later we add in the y predictions


# drop the straify category, not needed anymore 
for set_ in (X_train, X_test, train_data):
    set_.drop('living_area_cat', axis=1, inplace=True)


# combine all of the data into one big fat hairy beast.  use this for cleaning the data
# so we dont have any surprises regarding one hot encoding
X_train['TRAIN']=1          # 1 indicates its from the training data
X_test['TRAIN']=0           # 0 indicates its hold-out
sub_data['TRAIN']=-1        # -1 for the submissions data


# combine it all together
combined=pd.concat([X_train, X_test, sub_data])

#####
#####  Clean The Data
#####


 

# this will do the heavy lifting removing NaN(s), dropping columns, one hot encoding and feature engineering
combined = CleanData(combined)

# sendtofile(excluded_dir, 'combined.csv', combined, verbose=True)

#####
##### Pull the data apart into the proper data frames. Train, Test (aka holdout) and Submission
#####

# train - use to fit models
X_train = combined[combined['TRAIN']==1].copy()
X_train.drop('TRAIN', axis=1, inplace=True)

# sendtofile(excluded_dir, 'X_train.csv', X_train, verbose=True)


# test - use to evaluate model performance
X_test = combined[combined['TRAIN']==0].copy()
X_test.drop('TRAIN', axis=1, inplace=True)

# sub - use to submit the final answer for the kaggle cometition
X_sub = combined[combined['TRAIN']==-1].copy()
X_sub.drop('TRAIN', axis=1, inplace=True)

#all cols

train_cols = ['LotFrontage','LotArea','OverallQual','OverallCond','MasVnrArea','BsmtFinSF1','BsmtFinSF2','BsmtUnfSF','TotalBsmtSF','1stFlrSF','2ndFlrSF','LowQualFinSF','GrLivArea','BedroomAbvGr','KitchenAbvGr','TotRmsAbvGrd','Fireplaces','GarageCars','GarageArea','WoodDeckSF','OpenPorchSF','EnclosedPorch','3SsnPorch','ScreenPorch','PoolArea','MiscVal','MoSold','YrSold','IsRegularLotShape','IsLandLevel','IsLandSlopeGntl','IsElectricalSBrkr','IsGarageDetached','IsPavedDrive','HasShed','Neighborhood_Good','HouseAge','RemodelAge','NewRemodel','GarageAge','NewGarage','MSSubClass_20','MSSubClass_30','MSSubClass_40','MSSubClass_45','MSSubClass_50','MSSubClass_60','MSSubClass_70','MSSubClass_75','MSSubClass_80','MSSubClass_85','MSSubClass_90','MSSubClass_120','MSSubClass_160','MSSubClass_180','MSSubClass_190','MSZoning_C (all)','MSZoning_FV','MSZoning_RH','MSZoning_RL','MSZoning_RM','Street_Grvl','Street_Pave','LotShape_IR1','LotShape_IR2','LotShape_IR3','LotShape_Reg','LandContour_Bnk','LandContour_HLS','LandContour_Low','LandContour_Lvl','LotConfig_Corner','LotConfig_CulDSac','LotConfig_FR2','LotConfig_FR3','LotConfig_Inside','LandSlope_Gtl','LandSlope_Mod','LandSlope_Sev','Neighborhood_Blmngtn','Neighborhood_Blueste','Neighborhood_BrDale','Neighborhood_BrkSide','Neighborhood_ClearCr','Neighborhood_CollgCr','Neighborhood_Crawfor','Neighborhood_Edwards','Neighborhood_Gilbert','Neighborhood_IDOTRR','Neighborhood_MeadowV','Neighborhood_Mitchel','Neighborhood_NAmes','Neighborhood_NPkVill','Neighborhood_NWAmes','Neighborhood_NoRidge','Neighborhood_NridgHt','Neighborhood_OldTown','Neighborhood_SWISU','Neighborhood_Sawyer','Neighborhood_SawyerW','Neighborhood_Somerst','Neighborhood_StoneBr','Neighborhood_Timber','Neighborhood_Veenker','BldgType_1Fam','BldgType_2fmCon','BldgType_Duplex','BldgType_Twnhs','BldgType_TwnhsE','HouseStyle_1.5Fin','HouseStyle_1.5Unf','HouseStyle_1Story','HouseStyle_2.5Fin','HouseStyle_2.5Unf','HouseStyle_2Story','HouseStyle_SFoyer','HouseStyle_SLvl','RoofStyle_Flat','RoofStyle_Gable','RoofStyle_Gambrel','RoofStyle_Hip','RoofStyle_Mansard','RoofStyle_Shed','RoofMatl_CompShg','RoofMatl_Tar&Grv','RoofMatl_WdShake','RoofMatl_WdShngl','Exterior1st_AsbShng','Exterior1st_AsphShn','Exterior1st_BrkComm','Exterior1st_BrkFace','Exterior1st_CBlock','Exterior1st_CemntBd','Exterior1st_HdBoard','Exterior1st_MetalSd','Exterior1st_Plywood','Exterior1st_Stone','Exterior1st_Stucco','Exterior1st_VinylSd','Exterior1st_Wd Sdng','Exterior1st_WdShing','Exterior2nd_AsbShng','Exterior2nd_AsphShn','Exterior2nd_Brk Cmn','Exterior2nd_BrkFace','Exterior2nd_CBlock','Exterior2nd_CmentBd','Exterior2nd_HdBoard','Exterior2nd_ImStucc','Exterior2nd_MetalSd','Exterior2nd_Plywood','Exterior2nd_Stone','Exterior2nd_Stucco','Exterior2nd_VinylSd','Exterior2nd_Wd Sdng','Exterior2nd_Wd Shng','MasVnrType_BrkCmn','MasVnrType_BrkFace','MasVnrType_None','MasVnrType_Stone','Foundation_BrkTil','Foundation_CBlock','Foundation_PConc','Foundation_Slab','Foundation_Stone','Foundation_Wood','Heating_GasA','Heating_GasW','Heating_Grav','Heating_OthW','Heating_Wall','GarageType_2Types','GarageType_Attchd','GarageType_Basment','GarageType_BuiltIn','GarageType_CarPort','GarageType_Detchd','GarageType_NA','SaleType_COD','SaleType_CWD','SaleType_Con','SaleType_ConLD','SaleType_ConLI','SaleType_ConLw','SaleType_New','SaleType_Oth','SaleType_WD','SaleCondition_Abnorml','SaleCondition_AdjLand','SaleCondition_Alloca','SaleCondition_Family','SaleCondition_Normal','SaleCondition_Partial','Total_Qual_Cond','Condition1_INT','Condition2_INT','BsmtExposure_INT','BsmtFinType1_INT','BsmtFinType2_INT','CentralAir_INT','Electrical_INT','Functional_INT','GarageFinish_INT','PavedDrive_INT','BathroomCount']
# i like to keep the array of columns that i will be training/predicting with.  
# this gives me the chance to pull one out for testing if say a NaN or inf shows up in the process
# and its not so cumbersome to create.  
# open combined.csv, copy the first row, paste it into notepad and replace tab with ','
# dont forget to remove 'TRAIN' column from the list

#####
##### FIT THE MODELS
#####

# sendtofile(excluded_dir,"X_train.csv",X_train[train_cols], verbose=True)
# sendtofile(excluded_dir,"y_train.csv",pd.DataFrame(y_train), verbose=True)
# sendtofile(excluded_dir,"X_test.csv",X_test[train_cols], verbose=True)
# sendtofile(excluded_dir,"y_test.csv",pd.DataFrame(y_test), verbose=True)

X_train[train_cols].fillna(0,inplace=True)
X_test[train_cols].fillna(0,inplace=True)


###
### Random Forest optimization block
###
if False:  # set this to True so you can find the best params

    from sklearn.model_selection import RandomizedSearchCV
    # Number of trees in random forest
    #n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
    n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 6)]
    # Number of features to consider at every split
    max_features = ['auto', 'sqrt','log2']
    # Maximum number of levels in tree
    max_depth = [int(x) for x in np.linspace(2, 100, num = 10)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [2, 5, 10, 13, 17]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [1, 2, 4, 7 , 11 , 13]
    # Method of selecting samples for training each tree
    bootstrap = [True, False]
    # Create the random grid
    random_grid = {'n_estimators': n_estimators,
                'max_features': max_features,
                'max_depth': max_depth,
                'min_samples_split': min_samples_split,
                'min_samples_leaf': min_samples_leaf,
                'bootstrap': bootstrap}
    print("\nheres your pram random_grid")
    print(random_grid)
    print("\n")


    # Use the random grid to search for best hyperparameters
    # First create the base model to tune
    rf = RandomForestRegressor(random_state=9261774)
    # Random search of parameters, using 3 fold cross validation, 
    # search across 100 different combinations, and use all available cores
    rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 100, cv = 3, random_state=9261774, n_jobs = -1)
    # Fit the random search model
    rf_random.fit(X_train[train_cols], y_train)

    #print('\n\nBEST ESTIMATOR')
    #print (rf_random.best_estimator_ )
    print('\n\nBEST PARAMS')
    print (rf_random.best_params_ )
    #print('\n\nBEST SCORE')
    #print (rf_random.best_score_ )
    #print("\n\n")
    



###
### GradientBoostingRegressor optimization block
###
if False:  # set to True if you want to play with optimization
    from sklearn.model_selection import RandomizedSearchCV
    # Number of trees in random forest
    #n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
    n_estimators = [int(x) for x in np.linspace(start = 100, stop = 2000, num = 6)]
    # Number of features to consider at every split
    max_features = ['auto', 'sqrt', 'log2']
    # Maximum number of levels in tree
    # max_depth = [int(x) for x in np.linspace(3, 103, num = 11)]
    max_depth = [int(x) for x in np.linspace(2, 100, num = 10)]
    max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [2, 5, 10, 13, 21]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [1, 2, 4, 7 , 11]
    learning_rate = [0.01, 0.025, 0.05, 0.10, 0.075]
    # Method of selecting samples for training each tree
   

    # Create the random grid
    random_grid = {'n_estimators': n_estimators,
                'max_features': max_features,
                'learning_rate': learning_rate,
                'max_depth': max_depth,
                'min_samples_split': min_samples_split,
                'min_samples_leaf': min_samples_leaf}
    print("\nheres your param random_grid")
    print(random_grid)
    print("\n")


    # Use the random grid to search for best hyperparameters
    # First create the base model to tune
    gb = GradientBoostingRegressor(random_state=9261774)
    #print(gb.get_params().keys())
    

    # Random search of parameters, using 3 fold cross validation, 
    # search across 100 different combinations, and use all available cores
    gb_random = RandomizedSearchCV(estimator = gb, param_distributions = random_grid, n_iter = 100, cv = 3,random_state=9261774, n_jobs = -1)
    # Fit the random search model
    gb_random.fit(X_train[train_cols], y_train)

  

    #print('\n\nBEST ESTIMATOR')
    #print (gb_random.best_estimator_ )
    print('\n\nBEST PARAMS')
    print (gb_random.best_params_ )
    #print('\n\nBEST SCORE')
    #print (gb_random.best_score_ )
    #print("\n\n")
    
    #print(1/0) # hard stop if you like


#####
##### Create Submission
#####
if True:


       
    ###
    ### Linear Regression
    ###
    model_lr = LinearRegression(normalize=False)

    ### Fit the model
    model_lr.fit(X_train[train_cols], y_train)
    ## score the model
    train_score_lm=model_lr.score(X_train[train_cols], y_train)
    test_score_lm=model_lr.score(X_test[train_cols], y_test)
    print('lm training score     : ', train_score_lm)
    print('lm test score         : ', test_score_lm)


    predicted = pd.DataFrame(model_lr.predict(X_test[train_cols]))
    #predicted.columns=['PredictedSalePrice']
    expected = pd.DataFrame(y_test)
    #expected.columns=['ExpectedSalePrice']
    print('\nLinear Regression Evaluation')
    print('\n\npredicted')
    print(predicted.shape)
    print(predicted[:5])
    print('\n\nexpected')
    print(expected.shape)
    print(expected[:5])
    


    MSE = mean_squared_error(expected[:5], predicted[:5])
    print('\n\nMSE', MSE)
    
    plt.scatter(expected, predicted)
    plt.show()

    if False:
        ###
        ### Random Forest
        ###

        # BEST PARAMS
        # note, to get the best params, you need to run the optimization block
        # {'n_estimators': 480, 'min_samples_split': 2, 'min_samples_leaf': 1, 'max_features': 'sqrt', 'max_depth': None, 'bootstrap': False}
        model_rf = RandomForestRegressor(random_state=9261774, n_estimators=400, min_samples_split=2, min_samples_leaf=1, max_features='sqrt', max_depth=None, bootstrap=False)

        model_rf.fit(X_train[train_cols], y_train)
        train_score_rf=model_rf.score(X_train[train_cols], y_train)

        test_score_rf=model_rf.score(X_test[train_cols], y_test)
        print('rf training score     : ', train_score_rf)
        print('rf test score         : ', test_score_rf)


    if False:
        ###
        ### Gradient Boost
        ###

        # BEST PARAMS
        # note, to get the best params, you need to run the optimization block
        # {'n_estimators': 1620, 'min_samples_split': 2, 'min_samples_leaf': 2, 'max_features': 'sqrt', 'max_depth': 2, 'learning_rate': 0.025}
        model_gb = GradientBoostingRegressor(random_state=9261774,learning_rate=0.025, max_depth=2,min_samples_split=2, max_features="sqrt", min_samples_leaf=1, n_estimators=1620)
        model_gb.fit(X_train[train_cols], y_train)
        train_score_gb=model_gb.score(X_train[train_cols], y_train)
        test_score_gb=model_gb.score(X_test[train_cols], y_test)
        print('gb training score     : ', train_score_gb)
        print('gb test score         : ', test_score_gb)



    if False:
        ###
        ### Light Gradient Boost
        ###
        params = {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'metric': 'rmse',
            'max_depth': 8, 
            'learning_rate': 0.025,
            'verbose': 0,
            'num_leaves': 62}
        n_estimators = 300


        train_data = lgbm.Dataset(X_train[train_cols], label=y_train)
        test_data = lgbm.Dataset(X_test[train_cols], label=y_test)

        model_lgbm = lgbm.train(params, train_data, n_estimators, test_data)




print('\n\n')
print('*****')
print('***** end of script: eval_preds.py')
print('*****')
print('\n\n')


#   
#################################################