import pandas as pd
import pickle
from sqlalchemy import create_engine

import constants as C
from model import get_data


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
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    engine = create_engine(C.ENGINE)
    df = get_data(engine, booked=True)
    create_booked_table(engine, df, model)
