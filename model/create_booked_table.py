import numpy as np
import pickle
from sqlalchemy import create_engine

import constants as C
from model import get_data


def create_booked_table(engine, df, model):
    """
    Create Postgres table for the booked DataFrame and predictions and probabilities
    """
    df_new, X = model.pipeline.transform(df)
    probabilities = model.classifier.predict_proba(X)[:, 1]
    df_new["probability"] = np.around(probabilities, 2)
    df_new = prepare_data(df_new)
    df_new.to_sql("booked", engine, if_exists="replace", index=False)


def prepare_data(df):
    df["price"] = (50 * ((df["dropoff"] - df["pickup"]).dt.total_seconds() / 86400)).astype(int)
    df["insurance"] = df.apply(lambda row: insurance_mapping(row), axis=1)
    df["month"] = df["pickup"].dt.strftime("%B, %Y")
    df = convert_datetimes_to_strings(df, "created_at", "pickup", "dropoff")
    df[C.BINARY_YES_TO_NO] = df[C.BINARY_YES_TO_NO].replace({1: "Yes", 0: "No"})
    return df[C.APP_FEATURES_TO_KEEP].sort_values("pickup")


def insurance_mapping(row):
    if row["insurance_corporate"]:
        return "Corporate"
    elif row["insurance_personal"]:
        return "Personal"
    elif row["insurance_silvercar"]:
        return "Silvercar"
    return None


def convert_datetimes_to_strings(df, *args):
    for col_name in args:
        df[col_name] = df[col_name].dt.strftime("%m-%d-%y")
    return df


if __name__ == '__main__':
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    engine = create_engine(C.ENGINE)
    df = get_data(engine, booked=True)
    create_booked_table(engine, df.sample(200), model)
