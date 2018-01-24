## __init__.py

**__init__.py** contains all of the routes for my Flask application. When you run the app, the **booked** table
is retrieved from the PostgreSQL database, and the model is loaded from the **model.pkl** file. The data is sorted on
the probabilities, and the summary statistics are calculated.

When a user goes to the main index page ("/"), the summary stats and data frame are passed to the **index.html** file
to be rendered. When a user changes a drop-down selection, an AJAX request is sent to "/get_df_subset/" which slices
the data frame on the particular month and location. The data is then sent back to jQuery, which changes the elements
without rendering the page again.

When a user goes to the "/new-reservation/" page, the **new_reservations.html** file is rendered. When any of the fields
on the form are changed, an AJAX request is sent to "/calculate_probability/" which takes the inputs of the form and
calculate the cancellation probability. The probability, prediction, and price of the reservation are sent back, and the
stats at the top of the page are updated.

## templates/index.html

**index.html** is the HTML file that is rendered when users go to the app's index page ("/").

## templates/new_reservation.html

**index.html** is the HTML file that is rendered when users go to the "/new-reservation/" page.

## static/js/app.js

**app.js** is a JavaScript script for the two AJAX requests discussed above.

## static/css/styles.css

**styles.css** contains all of the styling for the two HTML pages.
