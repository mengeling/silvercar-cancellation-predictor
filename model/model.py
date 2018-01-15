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
        self.classifier = classifier

    def fit(self, df, y):
        """
        Transforms the training data and then fits the model
        """
        self.pipeline = Pipeline()
        X = self.pipeline.fit_transform(df, y)
        self.classifier.fit(X, y)

    def predict_proba(self, df):
        """
        Transforms the test data and then calculates probabilities
        """
        X = self.pipeline.transform(df.copy())
        return self.classifier.predict_proba(X)[:, 1]

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


def get_data(engine, booked=False):
    """
    Query and join 6 tables from Postgres database to get all of the features needed for the model
    """
    df_reservations = pd.read_sql_query(C.BOOKED_RESERVATIONS if booked else C.PAST_RESERVATIONS, con=engine)
    df_users = pd.read_sql_query(C.USERS, con=engine).set_index("id")
    df_users = df_users[~df_users.index.duplicated(keep='first')]
    return df_reservations.join(df_users, on="user_id", how="left").sort_values("pickup")


def create_booked_table(engine, df, model):
    """
    Create Postgres table for the booked DataFrame and predictions and probabilities
    """
    df["probability"] = model.predict_proba(df)
    df["prediction"] = model.predict(df)
    df["pickup"] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df["pickup"], 'D')
    df["dropoff"] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df["dropoff"], 'D')
    df["month"] = df["pickup"].dt.strftime('%B, %Y')
    df["price"] = 50 * ((df["dropoff"] - df["pickup"]).dt.total_seconds() / 86400)
    df.to_sql("booked", engine, if_exists="replace", index=False)


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    df = get_data(engine)
    df["current_state"] = ((df["current_state"] != "finished") & (df["current_state"] != "started")).astype(int)
    y = df.pop("current_state").values
    model = CancellationModel(LogisticRegression())
    model.fit(df, y)
    df_booked = get_data(engine, booked=True)
    create_booked_table(engine, df_booked, model)
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

