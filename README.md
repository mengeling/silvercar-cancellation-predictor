# Silvercar Cancellation Predictor

## Web Application

http://54.208.25.214/

## Background and Motivation

Silvercar is a startup rental car company that aspires to take the pain out of the rental car process,
so they have a number of different user-friendly policies:

- Users aren't charged for cancellations and no-shows
- Users don't have to create a Silvercar account to reserve a car
- Users don't have to enter credit card information to reserve a car

These policies gives customers a lot of flexibility, but it creates a business problem because
roughly 41% of their reservations aren't completed.

## Objective

I set out to create a model that could predict which reservations will be cancelled to help Silvercar:
- Better manage their fleet of cars (less cars sitting around unused)
- Improve short-term revenue forecasting
- Potentially identify opportunities to prevent cancellations

## Results

I achieved 80% accuracy, 84% precision, and 63% recall using XGBoost's implementation
of a gradient boosting classifier. In this case, recall is the number of actual cancellations divided
by the 


![Confusion Matrix](/images/confusion_matrix.png)




