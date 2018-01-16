import pandas as pd
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine

import constants as C


class Pipeline:
    def __init__(self):
        """
        Initialize pipeline by running all of the functions
        """
        self.y_mean = None
        self.d = defaultdict(list)
        self.scaler = StandardScaler()

    def fit_transform(self, df, y):
        """
        Fit and transform the training data
        """
        self.y_mean = y.mean()
        return self._run_pipeline(df, y)

    def transform(self, df):
        """
        Transform the test data
        """
        return self._run_pipeline(df)

    def transform_individual(self, df):
        """
        Transform a single reservation from the app demo
        """
        df = df.apply(pd.to_numeric, errors='ignore')
        df = self._create_date_features(df, individual=True)
        df = self._create_insurance_features(df, "Corporate", "Personal", "Silvercar")
        df = self._calculate_percent_cancelled(df)
        df = self._create_western_binary(df)
        df.replace({"Yes": 1, "No": 0, True: 1, False: 0}, inplace=True)
        df = self._filter_data(df)
        return self.scaler.transform(df)

    def _run_pipeline(self, df, y=None):
        """
        Make all of the requisite changes to the DataFrame
        """
        df = self._create_historical_features(df, y)
        df = self._create_date_features(df)
        df = self._create_binary_features(df)
        df = self._filter_data(df)
        return self.scaler.fit_transform(df) if y is not None else self.scaler.transform(df)

    def _create_date_features(self, df, individual=False):
        """
        Create all date-related features needed for the model
        """
        df = self._change_datetimes(df, individual, "pickup", "dropoff", "created_at")
        df = self._calculate_time_between(df,
                                          days_to_pickup=("pickup", "created_at"),
                                          trip_duration=("dropoff", "pickup"))
        df["weekend_pickup"] = df["pickup"].dt.dayofweek.isin([4, 5, 6]).astype(int)
        df["winter_pickup"] = df["pickup"].dt.month.isin([1, 12]).astype(int)
        return df

    @staticmethod
    def _change_datetimes(df, individual, *args):
        """
        Change timestamp columns from numbers to datetimes
        """
        if individual:
            for col_name in args:
                df[col_name] = pd.to_datetime(df[col_name])
        else:
            for col_name in args:
                df[col_name] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df[col_name], 'D')
        return df

    @staticmethod
    def _calculate_time_between(df, **kwargs):
        """
        Calculate the number of days between two datetime features
        """
        for k, (v1, v2) in kwargs.items():
            df[k] = (df[v1] - df[v2]).dt.total_seconds() / 86400
        return df

    @staticmethod
    def _create_binary_features(df):
        """
        Create all binary features needed for the model
        """
        df["used_promo"] = df["promo_code_id"].notnull().astype(int)
        df["used_referral"] = df["referral_code"].notnull().astype(int)
        df["credit_card"] = df["postal_code"].notnull().astype(int)
        df["web_booking"] = df["booking_application"].isin(C.WEB_APPS).astype(int)
        df["new_customer"] = (df["reservation_frequency"] != "repeat_customer").astype(int)
        df["western_pickup"] = ((df["time_zone"] == "pst") | (df["time_zone"] == "mst")).astype(int)
        return df

    def _create_historical_features(self, df, y):
        """
        Create all features related to user ride history
        """
        df["rides"] = self._get_past_ride_cnt(df, y)
        df["past_rides"] = df["rides"].apply(lambda lst: len(lst))
        df["past_cancellations"] = df["rides"].apply(lambda lst: sum(lst))
        df["past_percent_cancelled"] = df["past_cancellations"] / df["past_rides"]
        df["past_percent_cancelled"] = df["past_percent_cancelled"].fillna(self.y_mean)
        return df

    def _get_past_ride_cnt(self, df, y):
        """
        Iterate through user IDs to look up and append the user's past rides to the ride_history list. During training,
        the current reservation's label is added to the dictionary, so the result of the ride is recorded for the next
        time the user appears in the DataFrame. Returns the ride_history list to be added to the DataFrame.
        """
        ride_history = []
        for i, user_id in enumerate(df["user_id"]):
            ride_history.append(self.d[user_id].copy())
            if y is not None:
                self.d[user_id].append(y[i])
        return ride_history

    @staticmethod
    def _create_insurance_features(df, *args):
        """
        Create the three binary insurance features
        """
        for arg in args:
            col_name = "insurance_{}".format(arg.lower())
            df[col_name] = df["insurance"].iloc[0] == arg
        return df

    def _calculate_percent_cancelled(self, df):
        """
        Create the past_percent_cancelled and western_pickup features
        """
        if df["past_rides"].sum() == 0:
            df["past_percent_cancelled"] = self.y_mean
        else:
            df["past_percent_cancelled"] = df["past_cancellations"] / df["past_rides"]
        return df

    @staticmethod
    def _create_western_binary(df):
        """
        Create the past_percent_cancelled and western_pickup features
        """
        engine = create_engine(C.ENGINE)
        time_zone = engine.execute(C.GET_TIME_ZONE.format(df["location"].iloc[0])).fetchone()[0]
        df["western_pickup"] = (time_zone == "pst") | (time_zone == "mst")
        return df

    @staticmethod
    def _filter_data(df):
        """
        Filter out unnecessary columns and fill nulls
        """
        return df[C.FEATURES_TO_KEEP].fillna(0)
