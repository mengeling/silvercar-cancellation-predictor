## model.py

This script contains the custom model, **CancellationModel**, and **get_data**, a function that retrieves the data from
the PostgreSQL database. When **model.py** is executed, the **get_data** function is called, and **CancellationModel**
is instantiated and fit on the retrieved data. Afterwards, the fit model is pickled and dumped into the **model.pkl** file.

<br>

## pipeline.py

This file contains the custom pipeline class, **Pipeline**, which is used to fit and transform the data.
When the model is trained, the **fit_transform** method is called to transform the training data, so that
it can be fit on the model. The **transform** method is called when the model is making predictions on a number
of different reservations. The **transform_individual** method is called when the model is making a prediction on
a single data point from the web application.

<br>

## created_booked_table.py

When this script is executed, the model is loaded from **model.pkl** and booked reservations are
retrieved from the PostgreSQL database. Then the **create_booked_table** function is called, which uses the model object
to calculate probabilities before adding them to the data frame. After that, **prepare_data** is called to get the data formatted
in such a way that is presentable for the application. Finally, the data frame is written to the **booked** table in
the PostgreSQL database.

<br>

## constants.py

This file contains all of the SQL queries, data frame column names, and constant values that are
referenced throughout the repository.