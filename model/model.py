import pickle
import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression

import constants as C
from pipeline import Pipeline


class CancellationModel:
    def __init__(self, classifier):
        """
        Initialize model
        """
        self.pipeline = None
        self.classifer = classifier

    def fit(self, df, y):
        """
        Transforms the training data and then fits the model
        """
        self.pipeline = Pipeline()
        X = self.pipeline.fit_transform(df, y)
        self.classifer.fit(X, y)

    def predict_proba(self, df):
        """
        Transforms the test data and then calculates probabilities
        """
        X = self.pipeline.transform(df)
        return self.classifer.predict_proba(X)[:, 1]

    def predict(self, df):
        """
        Calls predict_proba function and then makes predictions based off of the chosen threshold
        """
        return (self.predict_proba(df) > C.THRESHOLD).astype(int)

    def score(self, df, y):
        """
        Calculates the accuracy of the model's predictions
        """
        return accuracy_score(y, self.predict(df))


def get_data(booked=False):
    """
    Query and join 6 tables from Postgres database to get all of the features needed for the model
    """
    df_reservations = pd.read_sql_query(C.BOOKED_RESERVATIONS if booked else C.PAST_RESERVATIONS, con=engine)
    df_users = pd.read_sql_query(C.USERS, con=engine)
    df_users = df_users[~df_users.index.duplicated(keep='first')]
    return df_reservations.join(df_users.set_index("id"), on="user_id", how="left")


def create_booked_table(df, model):
    """
    Create Postgres table for the booked DataFrame and predictions and probabilities
    """
    probabilities = model.predict_proba(df)
    predictions = (probabilities > C.THRESHOLD).astype(int)
    df["probabilities"] = probabilities
    df["predictions"] = predictions
    engine.execute("DROP TABLE IF EXISTS booked;")
    df.to_sql("booked", engine)


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    df = get_data()
    df["current_state"] = ((df["current_state"] != "finished") & (df["current_state"] != "started")).astype(int)
    y = df.pop("current_state").values
    model = CancellationModel(LogisticRegression())
    model.fit(df, y)
    df_booked = get_data(booked=True)
    create_booked_table(df_booked, model)
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

