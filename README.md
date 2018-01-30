# Rental Car Cancellation Predictor


&nbsp;
![Silvercar Logo](/images/silvercar_cars.jpg)
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


## MOEs (Measures of Effectiveness)

I chose accuracy as the MOE for reporting my model's performance because the classes are pretty balanced
(59% finished and 41% cancelled), and it's interpretable. I also used precision and recall
because they're both important for accomplishing my first two objectives. I chose not to use the raw F1
score though because I was looking for good precision and good recall, not just a good average of the two
(which is roughly what the F1 score calculates).

In this case, precision is the number of correctly identified cancellations divided by the number of predicted cancellations.
This is an important metric for fleet management because the number of incorrectly labeled cancellations need
to be minimized. If too many rides are incorrectly predicted to be cancelled, then the model would be informing Silvercar
that they don't need as many cars available as they actually do.

Recall is the number of correctly identified cancellations divided by the number of actual cancellations. If recall is too low
(i.e. the model isn't predicting enough cancellations), then the second objective won't be accomplished because revenue
will be overstated.


## MOPs (Measures of Performance)

The **reservations** table has about 460,000 rows, so I didn't have to worry about memory, storage,
or training time. All of the data can be stored on a single machine, and all of it can be loaded into a single machine's
memory. Every night, Silvercar could easily train the model on all of the historical reservations and make predictions
on the booked reservations.


## Results

Using a 50% threshold for predicting cancellations (meaning a cancellation is predicted when the cancellation probability is greater than 50%),
I achieved 80% accuracy, 84% precision, and 63% recall using XGBoost's implementation of a gradient boosting classifier.
As you can see in figure 1, the model is predicting significantly less cancellations than there actually were, which is why
recall is only 63%. This is problematic for revenue forecasting.

&nbsp;

![Confusion Matrix 1](/images/confusion_matrix.png)<br>**Figure 1**

&nbsp;


I lowered the same model's threshold to 40%, which resulted in 79% accuracy, 75% precision, and 72% recall.
This threshold gives a more even distribution of inaccurate predictions. Silvercar could take these predictions
and make more conservative estimates to calculate their revenue forecasts and determine the number of cars needed
at each location. I think coupling these predictions with historical data will prove to be more effective than solely
basing their projections on historical data.

&nbsp;

![Confusion Matrix 2](/images/confusion_matrix2.png)<br>**Figure 2**

<br>
<br>

![Roc Curve](/images/roc_curve.png)<br>**Figure 3**

&nbsp;


As for opportunities to prevent cancellations, figure 3 below illustrates the most important features
according to the final model.<sup>[1](#footnote1)</sup> Unsurprisingly most of the features are out of Silvercar's control,
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

![Feature Importances](/images/feature_importances.png)<br>**Figure 4**

&nbsp;

## Web Application

I made a prototype of a dashboard that can be used to monitor the expected number of cancellations
for each of Silvercar's locations. The new reservation page allows users to change different reservation features
to see how it affects the cancellation probability. Try it out here:

http://54.208.25.214/

http://54.208.25.214/new-reservation/


## Footnotes

<a name="footnote1">1</a>: Gradient boosting classifiers have misleading feature importances when
categorical and numerical features are mixed. In this case, the numerical features are weighted more heavily
even though all of the features were standardized. Feature importances have to be evaluated separately for the
numerical and categorical features.
