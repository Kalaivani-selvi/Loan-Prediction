# Loan Approval Prediction System

This project implements a loan approval prediction system using a machine learning model trained with logistic regression. The system is integrated into a Flask web application where users can input their details to get a prediction whether their loan application would be approved or not.

# Overview

This project demonstrates the application of machine learning in predicting loan approval decisions based on various factors such as income, credit history, education, etc. The machine learning model is trained using logistic regression on a labeled dataset, and the trained model is integrated into a Flask web application.

# Features

   -  Loan Approval Prediction: Users can input their details (gender, marital status, income, etc.) through a web form.
   - Integration with Flask: The backend is built with Flask, a Python web framework, to handle user requests and serve predictions.
   - Model Training and Evaluation: Includes scripts (train_model.py) for data preprocessing, model training, and evaluation metrics like accuracy, precision, and ROC AUC score.

# Dataset

The dataset used for training and testing the model (train.csv) includes various features related to loan applicants and their loan approval status. It's preprocessed to handle missing values, scale numeric features, and encode categorical features before training the model.
