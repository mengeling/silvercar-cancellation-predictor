import pickle
import pandas as pd
from sqlalchemy import create_engine


class Pipeline:
    def __init__(self):
        ''' initialize model '''
        self.vect = TfidfVectorizer()
        self.rf_text = RandomForestClassifier(n_estimators=50)
        self.rf_num = RandomForestClassifier(n_estimators=50)

    def fit(self, X_text, X_num, y):
        ''' fit model based on training data '''
        X_text = self.vect.fit_transform(X_text)
        self.rf_text.fit(X_text, y)
        self.rf_num.fit(X_num, y)

    def predict_proba(self, X_text, X_num):
        ''' calculate probability that item is fraud '''
        X_t = self.vect.transform(X_text)
        pred_txt = self.rf_text.predict_proba(X_t)[:, 1]
        pred_num = self.rf_num.predict_proba(X_num)[:, 1]
        return np.mean([pred_txt, pred_num], axis=0)

    def predict(self, X_text, X_num):
        ''' predict true/false for item '''
        proba = self.predict_proba(X_text, X_num)
        return (proba > THRESHOLD).astype(int)

    @staticmethod
    def get_datetime(series):
        return pd.to_datetime('1899-12-30') + pd.to_timedelta(series, 'D')

    @staticmethod
    def

def get_data():
    """
    Query PSQL database to get all of the features needed for the model
    """
    engine = create_engine('postgresql://mengeling:mengeling@localhost:5432/silvercar')
    df_reservations = pd.read_sql_query(
        "SELECT r.id, r.user_id, r.pickup_location_id, r.current_state, r.created_as_guest, r.local_rental, "
        "r.awards_referral_bonus, r.pickup, r.dropoff, r.created_at, r.updated_at, r.promo_code_id, "
        "r.booking_application, r.reservation_frequency, l.time_zone "
        "FROM reservations r "
        "LEFT JOIN locations l ON r.pickup_location_id = l.id "
        "WHERE current_state != 'booked' AND current_state != 'pending_agreement'",
        con=engine
    )
    df_users = pd.read_sql_query(
        "SELECT u.id, u.is_gds_user, u.referral_code, i.is_corporate, i.is_personal, i.is_silvercar, c.postal_code "
        "FROM users u "
        "LEFT JOIN insurance i ON u.id = i.user_id "
        "LEFT JOIN user_profile p ON u.id = p.user_id "
        "LEFT JOIN credit_cards c ON p.id = c.user_profile_id",
        con=engine
    )
    df_users = df_users[~df_users.index.duplicated(keep='first')]
    return df_reservations.join(df_users.set_index("id"), on="user_id", how="left")


if __name__ == '__main__':
    df = get_data()
    df["current_state"] = ((df["current_state"] != "finished") & (df["current_state"] != "started")).astype(int)
    y = df.pop("current_state").values
    model = CancellationModel()
    model.fit(df, y)
    print(df.head())
    # X, y = prepare_data(df)
    # lr = LogisticRegression()
    # lr.fit(X, y)
    # with open('model.pkl', 'wb') as f:
    #     pickle.dump(lr, f)
