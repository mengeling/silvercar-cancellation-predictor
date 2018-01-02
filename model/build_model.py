import pickle
import pandas as pd
from sklearn.linear_model import LogisticRegression


def get_datetime(series):
    return pd.to_datetime('1899-12-30') + pd.to_timedelta(series, 'D')


def create_days_to_pickup(df):
    df["pickup"] = get_datetime(df["pickup"])
    df["created_at"] = get_datetime(df["created_at"])
    df["days_to_pickup"] = df["pickup"] - df["created_at"]
    return df["days_to_pickup"].dt.total_seconds() / 86400


def load_reservations(filename, sample):
    df = pd.read_csv(filename)
    if sample:
        df = df.iloc[:40, :]
    df["days_to_pickup"] = create_days_to_pickup(df)
    df["used_promo"] = (df["promo_code_id"].notnull()).astype(int)
    df = df["user_id", "current_state", "days_to_pickup", "reservation_frequency", "used_promo"]
    df["current_state"] = df["current_state"].map({"cancelled": 1, "finished": 0})
    return pd.get_dummies(df)


def load_users(filename):
    df = pd.read_csv(filename)
    df = df[["id", "sign_in_count"]].set_index("id")
    return df


def merge_data(df1, df2):
    df = df1.join(df2, how="left", on="user_id")
    df.drop("user_id", axis=1, inplace=True)
    df.dropna(inplace=True)
    return df


def clean_data(sample=False):
    df_reservations = load_reservations('../data/silvercar_reservations.csv', sample)
    df_users = load_users('../data/silvercar_users.csv')
    return merge_data(df_reservations, df_users)


if __name__ == '__main__':
    df = clean_data()
    y = df.pop("current_state").values
    X = df.values
    lr = LogisticRegression()
    lr.fit(X, y)
    with open('model.pkl', 'wb') as f:
        pickle.dump(lr, f)
