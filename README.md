# Fraud-transaction-detection
Predicting fraud transactions using Gradient boost classifier

The problem is from a Kaggle competition - IEEE fraud transaction detection

XGBoost Classifier: 
Score - 0.933408 Rank - 65
Score - 0.928402 Rank - 547


You can download the dataset from here:

https://www.kaggle.com/c/14242/download-all

This repository contains python code for fraud transaction detection.

For the sake of comparision, I have used automl to train the model. The results are in AutoML_final.csv file. 

File description
1. ieeefrauddetection.py - python code
2. AutoML_final - contains results from google cloud automl.
3. Kaggle_Submission - contains results from XGBoost Classifier

Future work:
1. Wish to solve the same problem using other classifiers and compare the results.
2. To write the same code without using any library, or atleast PCA and Xgboost.

Optionally, you can have a look at following kernals. They are very informative. And I learnt a lot from them.
1. https://www.kaggle.com/kabure/extensive-eda-and-modeling-xgb-hyperopt#reducing-memory-usage
2. https://www.kaggle.com/xhlulu/ieee-fraud-xgboost-with-gpu-fit-in-40s
3. https://www.kaggle.com/cdeotte/xgb-fraud-with-magic-0-9600
