import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from collections import defaultdict
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

import constants as C


class Pipeline():
    def __init__(self):
        """
        Initialize model
        """
        self.df = None
        self.X = None
        self.X_booked = None
        self.y = None
        self.d = defaultdict(list)
        self.scaler = StandardScaler()

    def fit(self, df, y):
        self.df = df
        self.y = y
        self._create_date_features()
        self._create_binary_features()
        self._create_historical_features()
        self.X = self.scaler.fit_transform(self.df.values)

    def transform(self, df_booked):
        self.df = df_booked
        self._create_date_features()
        self._create_binary_features()
        self._create_historical_features(booked=True)
        self.df.drop("current_state", axis=1, inplace=True)
        self.X_booked = self.scaler.fit_transform(self.df.values)

    def _create_date_features(self):
        self._change_datetimes("pickup", "dropoff", "created_at")
        self._calculate_time_between(days_to_pickup=("pickup", "created_at"), trip_duration=("dropoff", "pickup"))
        self.df["weekend_pickup"] = self.df["pickup"].dt.dayofweek.isin([4, 5, 6]).astype(int)
        self.df["winter_pickup"] = self.df["pickup"].dt.month.isin([1, 12]).astype(int)
        self.df.drop(C.DATE_FEATURES_TO_DROP, axis=1, inplace=True)

    def _create_binary_features(self):
        self.df["used_promo"] = self.df["promo_code_id"].notnull().astype(int)
        self.df["web_booking"] = (self.df["booking_application"].isin(C.WEB_APPS)).astype(int)
        self.df["new_customer"] = (self.df["reservation_frequency"] != "repeat_customer").astype(int)
        self.df["used_referral"] = self.df["referral_code"].notnull().astype(int)
        self.df["credit_card"] = self.df["postal_code"].notnull().astype(int)
        self.df["western_pickup"] = ((self.df["time_zone"] == "pst") | (self.df["time_zone"] == "mst")).astype(int)
        self.df.fillna(value={"is_corporate": 0, "is_silvercar": 0, "is_personal": 0, "is_gds_user": 0}, inplace=True)
        self.df.rename(columns=C.INSURANCE_DICT, inplace=True)
        self.df.drop(C.OTHER_FEATURES_TO_DROP, axis=1, inplace=True)

    def _change_datetimes(self, *args):
        for col_name in args:
            self.df[col_name] = pd.to_datetime('1899-12-30') + pd.to_timedelta(self.df[col_name], 'D')

    def _calculate_time_between(self, **kwargs):
        for k, (v1, v2) in kwargs.items():
            self.df[k] = (self.df[v1] - self.df[v2]).dt.total_seconds() / 86400

    def _create_historical_features(self, booked=False):
        self._get_past_ride_cnt(booked)
        self.df["rides"] = self.ride_history
        self.df["past_rides"] = self.df["rides"].apply(lambda lst: len(lst))
        self.df["past_cancellations"] = self.df["rides"].apply(lambda lst: sum(lst))
        self.df["past_percent_cancelled"] = self.df["past_cancellations"] / self.df["past_rides"]
        self.df["past_percent_cancelled"] = self.df["past_percent_cancelled"].fillna(self.y.mean())
        self.df.drop(["user_id", "rides"], axis=1, inplace=True)

    def _get_past_ride_cnt(self, booked):
        self.ride_history = []
        for i, user_id in enumerate(self.df["user_id"]):
            self.ride_history.append(self.d[user_id].copy())
            if not booked:
                self.d[user_id].append(self.y[i])


def get_data(booked=False):
    """
    Query Postgres database to get all of the features needed for the model
    """
    engine = create_engine(C.ENGINE)
    query = C.BOOKED_RESERVATIONS if booked else C.PAST_RESERVATIONS
    df_reservations = pd.read_sql_query(query, con=engine)
    df_users = pd.read_sql_query(C.USERS, con=engine)
    df_users = df_users[~df_users.index.duplicated(keep='first')]
    return df_reservations.join(df_users.set_index("id"), on="user_id", how="left")


if __name__ == '__main__':
    df = get_data()
    df["current_state"] = ((df["current_state"] != "finished") & (df["current_state"] != "started")).astype(int)
    y = df.pop("current_state").values
    pipeline = Pipeline()
    pipeline.fit(df, y)
    df_booked = get_data(booked=True)
    pipeline.transform(df_booked)
