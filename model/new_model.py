import pickle
import pandas as pd
from sqlalchemy import create_engine
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# class DataType(BaseEstimator, TransformerMixin):
#     return

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
        "LEFT JOIN credit_cards c ON p.id = c.user_profile_id"
        , con=engine
    ).set_index("id")
    df_users = df_users[~df_users.index.duplicated(keep='first')]
    return df_reservations.join(df_users, on="user_id", how="left")


if __name__ == '__main__':
    df = get_data()

    print(df.head())
    print(df2.head())
    # X, y = prepare_data(df)
    # lr = LogisticRegression()
    # lr.fit(X, y)
    # with open('model.pkl', 'wb') as f:
    #     pickle.dump(lr, f)
