## __init__.py

This script contains all of the routes for the Flask application. When you run the app, the **booked** table
is retrieved from the PostgreSQL database, and the model is loaded from the **model.pkl** file. The data is sorted on
the probabilities, and the summary statistics are calculated.

When a user goes to the main index page ("/"), the summary stats and data frame are passed to the **index.html** file
to be rendered. When a user changes a drop-down selection, an AJAX request is sent to "/get_df_subset/" which slices
the data frame on the particular month and location. The data is then sent back to jQuery, which changes the elements
without rendering the page again.

When a user goes to the "/new-reservation/" page, the **new_reservations.html** file is rendered. When any of the fields
on the form are changed, an AJAX request is sent to "/calculate_probability/" which takes the inputs of the form and
calculates the cancellation probability. The probability, prediction, and price of the reservation are sent back to be
displayed on the top of the page.

<br>

## templates/index.html

This HTML file is rendered when users go to the app's index page ("/").

<br>

## templates/new_reservation.html

This HTML file is rendered when users go to the "/new-reservation/" page.

<br>

## static/js/app.js

This JavaScript script contains the two AJAX requests discussed above.

<br>

## static/css/styles.css

This stylesheet contains all of the styling for the two HTML pages.
