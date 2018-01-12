import pandas as pd
from collections import defaultdict
from sklearn.preprocessing import StandardScaler

import constants as C


class Pipeline:
    def __init__(self):
        """
        Initialize pipeline by running all of the functions
        """
        self.X = None
        self.d = defaultdict(list)
        self.scaler = StandardScaler()

    def fit_transform(self, df):
        self.X = df
        self._run_pipeline()
        return self.X, self.d

    def transform(self, df):
        self.X = df
        self._run_pipeline(booked=True)
        return self.X, self.d

    def _run_pipeline(self, booked=False):
        self._create_date_features()
        self._create_binary_features()
        self._create_historical_features(booked)
        self._filter_columns()
        self._fill_nulls()
        self.X = self.scaler.transform(self.X.values) if booked else self.scaler.fit_transform(self.X.values)

    def _create_date_features(self):
        """
        Create all date-related features needed for the model
        """
        self._change_datetimes("pickup", "dropoff", "created_at")
        self._calculate_time_between(days_to_pickup=("pickup", "created_at"), trip_duration=("dropoff", "pickup"))
        self.X["weekend_pickup"] = self.X["pickup"].dt.dayofweek.isin([4, 5, 6]).astype(int)
        self.X["winter_pickup"] = self.X["pickup"].dt.month.isin([1, 12]).astype(int)

    def _change_datetimes(self, *args):
        """
        Change timestamp columns from numbers to datetimes
        """
        for col_name in args:
            self.X[col_name] = pd.to_datetime('1899-12-30') + pd.to_timedelta(self.X[col_name], 'D')

    def _calculate_time_between(self, **kwargs):
        """
        Calculate the number of days between two datetime features
        """
        for k, (v1, v2) in kwargs.items():
            self.X[k] = (self.X[v1] - self.X[v2]).dt.total_seconds() / 86400

    def _create_binary_features(self):
        """
        Create all binary features needed for the model
        """
        self.X["used_promo"] = self.X["promo_code_id"].notnull().astype(int)
        self.X["used_referral"] = self.X["referral_code"].notnull().astype(int)
        self.X["credit_card"] = self.X["postal_code"].notnull().astype(int)
        self.X["web_booking"] = self.X["booking_application"].isin(C.WEB_APPS).astype(int)
        self.X["new_customer"] = (self.X["reservation_frequency"] != "repeat_customer").astype(int)
        self.X["western_pickup"] = ((self.X["time_zone"] == "pst") | (self.X["time_zone"] == "mst")).astype(int)

    def _create_historical_features(self, booked):
        """
        Create all features related to user ride history
        """
        self.X["rides"] = self._get_past_ride_cnt(booked)
        self.X["past_rides"] = self.X["rides"].apply(lambda lst: len(lst))
        self.X["past_cancellations"] = self.X["rides"].apply(lambda lst: sum(lst))
        self.X["past_percent_cancelled"] = self.X["past_cancellations"] / self.X["past_rides"]
        self.X["past_percent_cancelled"] = self.X["past_percent_cancelled"].fillna(self.y.mean())

    def _get_past_ride_cnt(self, booked):
        """
        Iterates through user IDs to look up and append the user's past rides to the ride_history list. During training,
        the current reservation's label is added to the dictionary, so the result of the ride is recorded for the next
        time the user appears in the DataFrame. Returns the ride_history list to be added to the DataFrame.
        """
        ride_history = []
        for i, user_id in enumerate(self.X["user_id"]):
            ride_history.append(self.d[user_id].copy())
            if not booked:
                self.d[user_id].append(self.y[i])
        return ride_history

    def _filter_columns(self):
        """
        Filter out columns that aren't used in the model
        """
        self.X = self.X[C.FEATURES_TO_KEEP]

    def _fill_nulls(self):
        """
        Fill null values
        """
        self.X.fillna(0, inplace=True)
