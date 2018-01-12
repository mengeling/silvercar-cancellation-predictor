import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

import constants as C


class CancellationModel():
    def __init__(self, classifier):
        """
        Initialize model
        """
        self.X = None
        self.y = None
        self.d = defaultdict(list)
        self.scaler = StandardScaler()
        self.classifer = classifier

    def fit(self, df, y):
        """
        Transforms the training data and then fits the model
        """
        self.X = df
        self.y = y
        self._create_date_features()
        self._create_binary_features()
        self._create_historical_features()
        self._filter_columns()
        self._fill_nulls()
        self.X = self.scaler.fit_transform(self.X.values)
        self.classifer.fit(self.X)
        return self

    def predict_proba(self, df):
        """
        Transforms the test data and then calculates probabilities
        """
        self.X = df
        self.y = None
        self._create_date_features()
        self._create_binary_features()
        self._create_historical_features()
        self._filter_columns()
        self._fill_nulls()
        self.X = self.scaler.transform(self.X.values)
        return self.classifer.predict_proba(self.X)

    def predict(self, df):
        """
        Calls predict_proba function and then makes predictions based off of the chosen threshold
        """
        probabilities = self.predict_proba(df)
        return (probabilities > C.THRESHOLD).astype(int)

    def score(self, df, y):
        """
        Calculates the accuracy of the model's predictions
        """
        predictions = self.predict(df)
        return

    def _create_date_features(self):
        """
        Create all date-related features needed for the model
        """
        self._change_datetimes("pickup", "dropoff", "created_at")
        self._calculate_time_between(days_to_pickup=("pickup", "created_at"), trip_duration=("dropoff", "pickup"))
        self.X["weekend_pickup"] = self.X["pickup"].dt.dayofweek.isin([4, 5, 6]).astype(int)
        self.X["winter_pickup"] = self.X["pickup"].dt.month.isin([1, 12]).astype(int)
        # self.X.drop(C.DATE_FEATURES_TO_DROP, axis=1, inplace=True)

    def _change_datetimes(self, *args):
        for col_name in args:
            self.X[col_name] = pd.to_datetime('1899-12-30') + pd.to_timedelta(self.X[col_name], 'D')

    def _calculate_time_between(self, **kwargs):
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
        # self.X.fillna(value={"is_corporate": 0, "is_silvercar": 0, "is_personal": 0, "is_gds_user": 0}, inplace=True)
        # self.X.rename(columns=C.INSURANCE_DICT, inplace=True)
        # self.X.drop(C.OTHER_FEATURES_TO_DROP, axis=1, inplace=True)

    def _create_historical_features(self):
        """
        Create all features related to user ride history
        """
        self.X["rides"] = self._get_past_ride_cnt()
        self.X["past_rides"] = self.X["rides"].apply(lambda lst: len(lst))
        self.X["past_cancellations"] = self.X["rides"].apply(lambda lst: sum(lst))
        self.X["past_percent_cancelled"] = self.X["past_cancellations"] / self.df["past_rides"]
        self.X["past_percent_cancelled"] = self.X["past_percent_cancelled"].fillna(self.y.mean())
        # self.X.drop(["user_id", "rides"], axis=1, inplace=True)

    def _get_past_ride_cnt(self):
        """
        Iterates through user IDs and adds
        :return:
        """
        ride_history = []
        for i, user_id in enumerate(self.X["user_id"]):
            ride_history.append(self.d[user_id].copy())
            if self.y:
                self.d[user_id].append(self.y[i])
        return ride_history

    def _filter_columns(self):


    def _fill_nulls(self):
        """
        Fill null values
        """
        self.X.fillna(
            value={"insurance_corporate": 0, "insurance_silvercar": 0, "insurance_personal": 0, "is_gds_user": 0},
            inplace=True
        )





def get_data(booked=False):
    """
    Query and join 6 tables from Postgres database to get all of the features needed for the model
    """
    engine = create_engine(C.ENGINE)
    df_reservations = pd.read_sql_query(C.BOOKED_RESERVATIONS if booked else C.PAST_RESERVATIONS, con=engine)
    df_users = pd.read_sql_query(C.USERS, con=engine)
    df_users = df_users[~df_users.index.duplicated(keep='first')].set_index("id")
    return df_reservations.join(df_users, on="user_id", how="left")


if __name__ == '__main__':
    df = get_data()
    df["current_state"] = ((df["current_state"] != "finished") & (df["current_state"] != "started")).astype(int)
    y = df.pop("current_state").values
    pipeline = CancellationModel()
    pipeline.fit(df, y)
    df_booked = get_data(booked=True)
    pipeline.predict(df_booked.drop("current_state", axis=1))
