# Fraud-transaction-detection
Problem Statement - Fraudulent means to dupe customers have been evolving ever since the inception of online transactions. Given two data sets containing the transaction and the identity details, predict the probability of fraud for a given transaction.

Major Highlights:
1. Cleansing and preprocessing was done using sklearn preprocessing library.
2. Performed Principal Component Analysis (PCA) to reduce the dimensions of the original dataset.
3. Used Bayesian optimization to get the best (hyper) parameters for XGBoost Classifier.
4. Used XGBoost Classifier to get the probability of a transaction being fraud.
5. For a comparative study, trained a binary classification model using Auto ML on Google Cloud Platform and compared the predictions obtained with those obtained from XGBoost classifier.

Score (AU ROC) - 0.933408 Rank - 65 (Using Extreme Gradient Boosted Decision Tree Classifier)
Score (AU ROC) - 0.928402 Rank - 547 (Using Auto ML)

Conclusion and Future Work - The XGBoost classifier definitely performed better than Auto ML. As future work would like to incorporate behavioural aspects of the customer. Thus enabling us to predict when a customer behaves erratically. This would further improve the accuracy of prediction by minimizing the falsely classified fraud transaction.

You can download the dataset from here:
https://www.kaggle.com/c/14242/download-all

File description
1. ieeefrauddetection.py - python code
2. AutoML_final - contains results from google cloud automl.
3. Kaggle_Submission - contains results from XGBoost Classifier

Optionally, you can have a look at following kernals. They are very informative. And I learnt a lot from them.
1. https://www.kaggle.com/kabure/extensive-eda-and-modeling-xgb-hyperopt#reducing-memory-usage
2. https://www.kaggle.com/xhlulu/ieee-fraud-xgboost-with-gpu-fit-in-40s
3. https://www.kaggle.com/cdeotte/xgb-fraud-with-magic-0-9600
