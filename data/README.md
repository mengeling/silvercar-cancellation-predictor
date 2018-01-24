# Data

None of the data has been pushed to this remote repository because all of it is private Silvercar data.
The AWS EC2 instance that is hosting the app only has access to the **booked** table, which is a sample of 200 old
reservations, because the table is displayed on the app.

## create_tables.py

I received the data in CSV and TXT files, so this script writes all of it to the PostgreSQL database, **silvercar**.