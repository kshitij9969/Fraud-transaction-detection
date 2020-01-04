# -*- coding: utf-8 -*-
"""IEEEFraudDetection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AUqXhWwmzaoizfmZKihEFgBUbIo1vzs6
"""
# -*- coding: utf-8 -*-
"""IEEEFraudDetection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AUqXhWwmzaoizfmZKihEFgBUbIo1vzs6

This python code uses gradient boost to classify transactions as fraud or valid. Hyper optimization is used to find the best hyper parameters for the classifier.
"""

# Importing all required libraries.
import numpy as np
import pandas as pd

# Preprocessing, modelling and evaluating
from sklearn import preprocessing
# Metrics for evaluating the performance of the model
from sklearn.metrics import confusion_matrix, roc_auc_score
# Importing Kfold for validation of the model
from sklearn.model_selection import StratifiedKFold, cross_val_score, KFold

# Importing the classifier for classfying the frauds and valid transactions
from xgboost import XGBClassifier
import xgboost as xgb

## Hyperopt modules
# Hyperoptfor Bayesian optimization. To get best hyper parameters for the Xgboost classifier
from hyperopt import fmin, hp, tpe, Trials, space_eval, STATUS_OK, STATUS_RUNNING

# (Optional if you are using collaboratory)
# Mounting the drive and getting the dataset

'''from google.colab import drive
drive.mount('/content/drive')
!ls '/content/drive/My Drive/ieee-fraud-detection'
'''
"""Modelling"""

# Import the datasets.
transactions = pd.read_csv('/content/drive/My Drive/ieee-fraud-detection/train_transaction.csv')
transactions_test = pd.read_csv('/content/drive/My Drive/ieee-fraud-detection/test_transaction.csv')
identity = pd.read_csv('/content/drive/My Drive/ieee-fraud-detection/train_identity.csv')
identity_test = pd.read_csv('/content/drive/My Drive/ieee-fraud-detection/test_identity.csv')

# Aparently, there is some mismatch in the column names in test_identity and train_identity
# In one of them it is id_01 and other is id-01 so we make it consistent.
for i in range(1,39):
  if i < 10:
    identity_test.columns.values[[i]]='id_0' + str(i)
  else:
    identity_test.columns.values[[i]]='id_'+str(i)

sample_submission = pd.read_csv('/content/drive/My Drive/ieee-fraud-detection/sample_submission.csv', index_col='TransactionID')

train_data = transactions.merge(identity, how='left', left_index=True, right_index=True, on='TransactionID')
test_data = transactions_test.merge(identity_test, how='left', left_index=True, right_index=True, on='TransactionID')

# Mapping emails
# https://www.kaggle.com/c/ieee-fraud-detection/discussion/100499#latest-579654
emails = {'gmail': 'google', 'att.net': 'att', 'twc.com': 'spectrum', 
          'scranton.edu': 'other', 'optonline.net': 'other', 'hotmail.co.uk': 'microsoft',
          'comcast.net': 'other', 'yahoo.com.mx': 'yahoo', 'yahoo.fr': 'yahoo',
          'yahoo.es': 'yahoo', 'charter.net': 'spectrum', 'live.com': 'microsoft', 
          'aim.com': 'aol', 'hotmail.de': 'microsoft', 'centurylink.net': 'centurylink',
          'gmail.com': 'google', 'me.com': 'apple', 'earthlink.net': 'other', 'gmx.de': 'other',
          'web.de': 'other', 'cfl.rr.com': 'other', 'hotmail.com': 'microsoft', 
          'protonmail.com': 'other', 'hotmail.fr': 'microsoft', 'windstream.net': 'other', 
          'outlook.es': 'microsoft', 'yahoo.co.jp': 'yahoo', 'yahoo.de': 'yahoo',
          'servicios-ta.com': 'other', 'netzero.net': 'other', 'suddenlink.net': 'other',
          'roadrunner.com': 'other', 'sc.rr.com': 'other', 'live.fr': 'microsoft',
          'verizon.net': 'yahoo', 'msn.com': 'microsoft', 'q.com': 'centurylink', 
          'prodigy.net.mx': 'att', 'frontier.com': 'yahoo', 'anonymous.com': 'other', 
          'rocketmail.com': 'yahoo', 'sbcglobal.net': 'att', 'frontiernet.net': 'yahoo', 
          'ymail.com': 'yahoo', 'outlook.com': 'microsoft', 'mail.com': 'other', 
          'bellsouth.net': 'other', 'embarqmail.com': 'centurylink', 'cableone.net': 'other', 
          'hotmail.es': 'microsoft', 'mac.com': 'apple', 'yahoo.co.uk': 'yahoo', 'netzero.com': 'other', 
          'yahoo.com': 'yahoo', 'live.com.mx': 'microsoft', 'ptd.net': 'other', 'cox.net': 'other',
          'aol.com': 'aol', 'juno.com': 'other', 'icloud.com': 'apple'}

us_emails = ['gmail', 'net', 'edu']

for c in ['P_emaildomain', 'R_emaildomain']:
    train_data[c + '_bin'] = train_data[c].map(emails)
    test_data[c + '_bin'] = test_data[c].map(emails)
    
    train_data[c + '_suffix'] = train_data[c].map(lambda x: str(x).split('.')[-1])
    test_data[c + '_suffix'] = test_data[c].map(lambda x: str(x).split('.')[-1])
    
    train_data[c + '_suffix'] = train_data[c + '_suffix'].map(lambda x: x if str(x) not in us_emails else 'us')
    test_data[c + '_suffix'] = test_data[c + '_suffix'].map(lambda x: x if str(x) not in us_emails else 'us')

# Label encoding
for col in train_data.drop('isFraud', axis=1).columns:
   if train_data[col].dtype=='object': 
        lbl = preprocessing.LabelEncoder()
        lbl.fit(list(train_data[col].values) + list(test_data[col].values))
        train_data[col] = lbl.transform(list(train_data[col].values))

for col in test_data.columns:
       if test_data[col].dtype=='object':
           lbl = preprocessing.LabelEncoder()
           lbl.fit(list(train_data[col].values))
           test_data[col] = lbl.transform(list(test_data[col].values))
           
           
test_data['isFraud'] = 'test'
df = pd.concat([train_data, test_data], axis=0, sort=False )
df = df.reset_index()
df = df.drop('index', axis=1)

# PCA on df.
def PCA(df, cols, n_components, prefix='PCA_', rand_seed=4):
    pca = PCA(n_components=n_components, random_state=rand_seed)

    principalComponents = pca.fit_transform(df[cols])

    principalDf = pd.DataFrame(principalComponents)

    df.drop(cols, axis=1, inplace=True)

    principalDf.rename(columns=lambda x: str(prefix)+str(x), inplace=True)

    df = pd.concat([df, principalDf], axis=1)
    
    return df


mas_v = train_data.columns[55:394]

from sklearn.preprocessing import minmax_scale
from sklearn.decomposition import PCA

for col in mas_v:
    df[col] = df[col].fillna((df[col].min() - 2))
    df[col] = (minmax_scale(df[col], feature_range=(0,1)))

    
df = PCA(df, mas_v, prefix='PCA_V_', n_components=30)


train_data, test_data = df[df['isFraud'] != 'test'], df[df['isFraud'] == 'test'].drop('isFraud', axis=1)

train_data.shape

'''
Variables:
    1. X_train: matrix of independent features.
    2. y_train: matrix of dependent variable.
    3. X_test: matrix of testing independent features.
    

'''


X_train = train_data.sort_values('TransactionDT').drop(['isFraud', 
                                                      'TransactionDT', 
                                                      ],
                                                     axis=1)
                                                     
y_train = train_data.sort_values('TransactionDT')['isFraud'].astype(bool)


X_test = test_data.sort_values('TransactionDT').drop(['TransactionDT'
                                                   ], 
                                                   axis=1)
test_data = test_data[["TransactionDT"]]

'''Exporting the dataset to train and test the model on google cloud.'''
X_test.to_csv(path_or_buf='/content/drive/My Drive/ieee-fraud-detection/Xtest.csv')

X_train.to_csv(path_or_buf='/content/drive/My Drive/ieee-fraud-detection/X_train.csv')

# Downloading the csv files
from google.colab import files

files.download('/content/drive/My Drive/ieee-fraud-detection/Xtrain.csv')


# Peforming hyper optmization
from sklearn.model_selection import KFold, TimeSeriesSplit
from sklearn.metrics import roc_auc_score
from sklearn.metrics import make_scorer

def objective(params):
    params = {
        'max_depth': int(params['max_depth']),
        'gamma': "{:.3f}".format(params['gamma']),
        'subsample': "{:.2f}".format(params['subsample']),
        'reg_alpha': "{:.3f}".format(params['reg_alpha']),
        'reg_lambda': "{:.3f}".format(params['reg_lambda']),
        'learning_rate': "{:.3f}".format(params['learning_rate']),
        'num_leaves': '{:.3f}'.format(params['num_leaves']),
        'colsample_bytree': '{:.3f}'.format(params['colsample_bytree']),
        'min_child_samples': '{:.3f}'.format(params['min_child_samples']),
        'feature_fraction': '{:.3f}'.format(params['feature_fraction']),
        'bagging_fraction': '{:.3f}'.format(params['bagging_fraction'])
    }
    print(f"params = {params}")
    # Typically, we choose K = 10.
    # Run it 10 times by training the model and calculating the mean score.
    SKfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=1)
    time_series_split = TimeSeriesSplit(n_splits=10)
    y_preds = np.zeros(sample_submission.shape[0])
    score_mean = 0 # To store CV score
    # Iterate and run the classifier.
    for train_index, validate_index in time_series_split.split(X_train, y_train):
        classifier = xgb.XGBClassifier(
            n_estimators=600, random_state=4, verbose=True, 
            tree_method='gpu_hist', 
            **params
        )

        train_x, train_validate_x = X_train.iloc[train_index, :], X_train.iloc[validate_index, :]
        train_y, train_validate_y = y_train.iloc[train_index], y_train.iloc[validate_index]
        
        classifier.fit(train_x, train_y)
        score = make_scorer(roc_auc_score, needs_proba=True)(classifier, train_validate_x, train_validate_y)
        score_mean += score
        print(f'Score_final: {score_mean / 10}')
    del train_x, train_validate_x, train_y, train_validate_y, classifier, score
    return -(score_mean / 10)


space = {
    'max_depth': hp.quniform('max_depth', 5, 20, 1),
    'reg_alpha':  hp.uniform('reg_alpha', 0.01, 0.4),
    'reg_lambda': hp.uniform('reg_lambda', 0.01, .4),
    'learning_rate': hp.uniform('learning_rate', 0.01, 0.2),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.3, .9),
    'gamma': hp.uniform('gamma', 0.01, .7),
    'num_leaves': hp.choice('num_leaves', list(range(20, 250, 10))),
    'min_child_samples': hp.choice('min_child_samples', list(range(100, 250, 10))),
    'subsample': hp.choice('subsample', [0.2, 0.4, 0.5, 0.6, 0.7, .8, .9]),
    'feature_fraction': hp.uniform('feature_fraction', 0.4, .8),
    'bagging_fraction': hp.uniform('bagging_fraction', 0.4, .9)
}

# Set algoritm parameters
# Running it for max 10 evals
best = fmin(fn=objective,
            space=space,
            algo=tpe.suggest,
            max_evals=10)

# Get the best hyper parameters
best_params = space_eval(space, best)
print(best_params)

# Pass the best parameters and run the XGBClassifier
best_params['max_depth'] = int(best_params['max_depth'])
classifier = xgb.XGBClassifier(
    n_estimators=300,
    **best_params,
    tree_method='gpu_hist'
)

classifier.fit(X_train, y_train)

y_preds = classifier.predict_proba(X_test)[:,1]

print(y_preds)