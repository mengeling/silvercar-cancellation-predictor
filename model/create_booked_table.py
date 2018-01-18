import pandas as pd
import pickle
from sqlalchemy import create_engine

import constants as C
from model import get_data


def create_booked_table(engine, df, model):
    """
    Create Postgres table for the booked DataFrame and predictions and probabilities
    """
    df_new, X = model.pipeline.transform(df)
    df_new["probability"] = model.classifier.predict_proba(X)[:, 1]
    df_new["prediction"] = (df_new["probability"] > C.THRESHOLD).astype(int)
    df_new["month"] = df["pickup"].dt.strftime('%B, %Y')
    df_new["price"] = 50 * ((df_new["dropoff"] - df_new["pickup"]).dt.total_seconds() / 86400)
    df_new["insurance"] = df_new[["insurance_corporate", "insurance_personal", "insurance_silvercar"]].idxmax(axis=1)
    df_new["insurance"] = df_new["insurance"].map({"insurance_personal": "Personal", "insurance_corporate": "Corporate",
                                                   "insurance_silvercar": "Silvercar", None: "None"})
    df_new = df_new[C.APP_FEATURES_TO_KEEP].sort_values("pickup")
    df_new.sort_values("pickup").to_sql("booked", engine, if_exists="replace", index=False)


if __name__ == '__main__':
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    engine = create_engine(C.ENGINE)
    df = get_data(engine, booked=True)
    create_booked_table(engine, df.sample(200), model)
