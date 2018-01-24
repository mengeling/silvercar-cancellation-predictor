THRESHOLD = 0.4


DAILY_RATE = 50


ENGINE = "postgresql://mengeling:mengeling@localhost:5432/silvercar"


MODEL_FEATURES_TO_KEEP = ["created_as_guest", "local_rental", "awards_referral_bonus", "is_gds_user",
                          "insurance_corporate", "insurance_personal", "insurance_silvercar", "days_to_pickup",
                          "trip_duration", "weekend_pickup", "winter_pickup", "used_promo", "credit_card",
                          "web_booking", "past_rides", "past_cancellations", "past_percent_cancelled", "pickup_dow",
                          "modified_profile", "western_pickup", "midday_pickup"]


APP_FEATURES_TO_KEEP = ["name", "airport_code", "created_at", "pickup", "dropoff", "insurance", "price", "past_rides",
                        "past_cancellations", "created_as_guest", "credit_card", "awards_referral_bonus", "used_promo",
                        "modified_profile", "is_gds_user", "local_rental", "web_booking", "probability", "month"]


BINARY_TO_YES_NO = ["credit_card", "awards_referral_bonus",	"used_promo", "modified_profile",
                    "is_gds_user", "local_rental", "web_booking", "created_as_guest"]


APP_COL_NAMES = {"airport_code": "Location", "created_at": "Created", "pickup": "Pickup", "dropoff": "Dropoff",
                 "insurance": "Insurance", "price": "Price ($)", "past_rides": "Past Rides",
                 "past_cancellations": "Past Rides Cancelled", "credit_card": "Credit Card",
                 "awards_referral_bonus": "Used Referral", "used_promo": "Used Promo",
                 "created_as_guest": "Guest", "modified_profile": "Modified Profile", "is_gds_user": "GDS User",
                 "local_rental": "Local Rental", "web_booking": "Web Booking",
                 "probability": "Cancellation Probability"}


PAST_RESERVATIONS = (
    "SELECT r.user_id, r.current_state, r.created_as_guest, r.local_rental, r.awards_referral_bonus, "
    "r.pickup, r.dropoff, r.created_at, r.promo_code_id, r.booking_application, r.reservation_frequency, l.time_zone "
    "FROM reservations r "
    "LEFT JOIN locations l ON r.pickup_location_id = l.id "
    "WHERE r.current_state != 'booked' AND r.current_state != 'pending_agreement' "
    "ORDER BY r.pickup ASC;"
)


BOOKED_RESERVATIONS = (
    "SELECT r.user_id, r.created_as_guest, r.local_rental, r.awards_referral_bonus, r.pickup, r.dropoff, r.created_at, "
    "r.promo_code_id, r.booking_application, r.reservation_frequency, l.time_zone, l.name, l.airport_code "
    "FROM reservations r "
    "LEFT JOIN locations l ON r.pickup_location_id = l.id "
    "WHERE r.current_state != 'booked' AND r.current_state != 'pending_agreement' "
    "AND r.pickup >= 41640 AND r.pickup < 41821 "
    "ORDER BY r.pickup ASC;"
)


USERS = (
    "SELECT u.id, u.is_gds_user, u.referral_code, u.created_at, u.updated_at, c.postal_code, "
    "i.insurance_corporate, i.insurance_personal, i.insurance_silvercar "
    "FROM users u "
    "LEFT JOIN insurance i ON u.id = i.user_id "
    "LEFT JOIN user_profile p ON u.id = p.user_id "
    "LEFT JOIN credit_cards c ON p.id = c.user_profile_id;"
)


GET_TIME_ZONE = (
    "SELECT time_zone FROM locations WHERE name = '{}'"
)


DATE_COLS = ["pickup", "dropoff", "created_at", "updated_at", "created_at_user"]


DATE_COLS_SHORT = ["pickup", "dropoff", "created_at"]
