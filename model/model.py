import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression


def prepare_data(df):
    df = pd.get_dummies(df)
    y = df.pop("current_state").values
    X = df.values
    return X, y


def merge_data(df1, df2):
    df = df1.join(df2, how="left", on="user_id")
    df.drop("user_id", axis=1, inplace=True)
    return df.dropna()


def load_users(filename):
    df = pd.read_csv(filename)
    return df[["id", "sign_in_count"]].set_index("id")


def get_datetime(series):
    return pd.to_datetime('1899-12-30') + pd.to_timedelta(series, 'D')


def create_days_to_pickup(df):
    df["pickup"] = get_datetime(df["pickup"])
    df["created_at"] = get_datetime(df["created_at"])
    return (df["pickup"] - df["created_at"]).dt.total_seconds() / 86400


def load_reservations(filename):
    df = pd.read_csv(filename)
    df["days_to_pickup"] = create_days_to_pickup(df)
    df["used_promo"] = (df["promo_code_id"].notnull()).astype(int)
    df["current_state"] = df["current_state"].map({"cancelled": 1, "finished": 0})
    return df[["user_id", "current_state", "days_to_pickup", "reservation_frequency", "used_promo"]]


def get_data():
    df_reservations = load_reservations('../data/silvercar_reservations.csv')
    df_users = load_users('../data/silvercar_users.csv')
    return merge_data(df_reservations, df_users)


if __name__ == '__main__':
    df = get_data()
    X, y = prepare_data(df)
    lr = LogisticRegression()
    lr.fit(X, y)
    with open('model.pkl', 'wb') as f:
        pickle.dump(lr, f)
