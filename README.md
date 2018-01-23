# Rental Car Cancellation Predictor


&nbsp;
![Silvercar Logo](/images/image.jpg)
&nbsp;

[Click Here To Try The App!](http://54.208.25.214/)
<br>

## Background and Motivation

Silvercar is a rental car startup that aspires to take the pain out of the rental car process,
so they have a number of different user-friendly policies:

- Users aren't charged for cancellations and no-shows
- Users don't have to create a Silvercar account to reserve a car
- Users don't have to enter credit card information to reserve a car

These policies give customers a lot of flexibility, but they've created a business problem because
roughly 41% of their reservations aren't completed.


## Objective

I set out to create a model that can predict the reservations that will be cancelled to help Silvercar:
- Better manage their fleet of cars at each location
- Improve short-term revenue forecasting
- Potentially identify opportunities to prevent cancellations


## Results

I achieved 80% accuracy, 84% precision, and 63% recall using XGBoost's implementation
of a gradient boosting classifier. The confusion matrix in figure 1 shows the number of correctly and incorrectly
labeled cancellations and finished rides.


&nbsp;

![Confusion Matrix 1](/images/confusion_matrix.png)<br>**Figure 1**

&nbsp;


In figure 1, I'm using a 0.5 threshold to make predictions, which means that if the cancellation probability
is greater than 50%, then the model predicts the reservation will be cancelled.
The recall (the number of correctly identified cancellations divided
by the number of actual cancellations) is only 63%, which could be problematic for
revenue forecasting because at the 0.5 threshold, the model is predicting less cancellations than there actually were.
If the model isn't predicting enough cancellations, then the predicted revenue would be overstated.

Conversely, the lower number of predicted cancellations is good from a fleet management perspective
because the model is being more conservative by predicting more rides will be finished and thus
informing Silvercar that they need to have more cars available.

Because of these conflicting interests, I propose that Silvercar uses one threshold for
revenue forecasting and another for fleet management. For revenue forecasting, I lowered the
threshold to 0.35 and increased recall to 77% as you can see in the increased number of correctly
labeled cancellations in figure 2. At that threshold, accuracy was 78% and
precision was 72%.


&nbsp;

![Confusion Matrix 2](/images/confusion_matrix2.png)<br>**Figure 2**

&nbsp;


As for opportunities to prevent cancellations, figure 3 below illustrates the most important features
according to the final model. Unsurprisingly most of the features are out of Silvercar's control,
but promotions could be useful because users are less likely to cancel when applying promo codes
to their reservations. We would need to conduct cost-benefit analysis, but offering promotions to
users that are more likely to cancel could yield positive results.

Silvercar tries to bother its customers as little as possible, but they could start to send their
customers email reminders for upcoming trips that ask the customers to confirm or cancel their
reservation. This wouldn't necessarily reduce cancellations, but it could complement the model well.
Silvercar would have more notice of the cancellations, and they wouldn't need to rely on the model
for as many predictions.

Silvercar could also start to send out cancellation surveys, so they could segment the cancellations
based off of the various cancellation reasons.

&nbsp;

![Feature Importances](/images/feature_importances.png)<br>**Figure 3**

&nbsp;

## Web Application

I made a prototype of a dashboard that can be used to monitor the expected number of cancellations
for each of Silvercar's locations. The new reservation page allows users to change different reservation features
to see how it affects the cancellation probability. Try it out here:

http://54.208.25.214/

http://54.208.25.214/new-reservation/
