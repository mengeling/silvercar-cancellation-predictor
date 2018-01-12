ENGINE = "postgresql://mengeling:mengeling@localhost:5432/silvercar"

PAST_RESERVATIONS = (
    "SELECT r.user_id, r.current_state, r.created_as_guest, r.local_rental, r.awards_referral_bonus, "
    "r.pickup, r.dropoff, r.created_at, r.promo_code_id, r.booking_application, r.reservation_frequency, l.time_zone "
    "FROM reservations r "
    "LEFT JOIN locations l ON r.pickup_location_id = l.id "
    "WHERE current_state != 'booked' AND current_state != 'pending_agreement'"
)

BOOKED_RESERVATIONS = (
    "SELECT r.user_id, r.current_state, r.created_as_guest, r.local_rental, r.awards_referral_bonus, r.pickup, "
    "r.dropoff, r.created_at, r.promo_code_id, r.booking_application, r.reservation_frequency, l.time_zone "
    "FROM reservations r "
    "LEFT JOIN locations l ON r.pickup_location_id = l.id "
    "WHERE current_state = 'booked'"
)

USERS = (
    "SELECT u.id, u.is_gds_user, u.referral_code, i.is_corporate, i.is_personal, i.is_silvercar, c.postal_code "
    "FROM users u "
    "LEFT JOIN insurance i ON u.id = i.user_id "
    "LEFT JOIN user_profile p ON u.id = p.user_id "
    "LEFT JOIN credit_cards c ON p.id = c.user_profile_id"
)

DATE_FEATURES_TO_DROP = ["pickup", "dropoff", "created_at", "updated_at"]

WEB_APPS = ["web", "web-desktop", "web-mobile", "web-tablet"]

INSURANCE_DICT = {"is_corporate": "insurance_corp", "is_silvercar": "insurance_silvercar",
                  "is_personal": "insurance_personal"}

OTHER_FEATURES_TO_DROP = ["promo_code_id", "booking_application", "reservation_frequency", "referral_code",
                          "postal_code", "time_zone"]