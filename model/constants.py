THRESHOLD = 0.5

WEB_APPS = ["web", "web-desktop", "web-mobile", "web-tablet"]

FEATURES_TO_KEEP = ["created_as_guest", "local_rental", "awards_referral_bonus", "is_gds_user", "insurance_corporate",
                    "insurance_personal", "insurance_silvercar", "days_to_pickup", "trip_duration", "weekend_pickup",
                    "winter_pickup", "used_promo", "used_referral", "credit_card", "web_booking", "new_customer",
                    "western_pickup", "past_rides", "past_cancellations", "past_percent_cancelled"]

ENGINE = "postgresql://mengeling:mengeling@localhost:5432/silvercar"

PAST_RESERVATIONS = (
    "SELECT r.user_id, r.current_state, r.created_as_guest, r.local_rental, r.awards_referral_bonus, "
    "r.pickup, r.dropoff, r.created_at, r.promo_code_id, r.booking_application, r.reservation_frequency, l.time_zone "
    "FROM reservations r "
    "LEFT JOIN locations l ON r.pickup_location_id = l.id "
    "WHERE current_state != 'booked' AND current_state != 'pending_agreement';"
)

BOOKED_RESERVATIONS = (
    "SELECT r.user_id, r.created_as_guest, r.local_rental, r.awards_referral_bonus, r.pickup, r.dropoff, "
    "r.created_at, r.promo_code_id, r.booking_application, r.reservation_frequency, l.time_zone, l.name "
    "FROM reservations r "
    "LEFT JOIN locations l ON r.pickup_location_id = l.id "
    "WHERE current_state = 'booked';"
)

USERS = (
    "SELECT u.id, u.is_gds_user, u.referral_code, i.insurance_corporate, i.insurance_personal, "
    "i.insurance_silvercar, c.postal_code "
    "FROM users u "
    "LEFT JOIN insurance i ON u.id = i.user_id "
    "LEFT JOIN user_profile p ON u.id = p.user_id "
    "LEFT JOIN credit_cards c ON p.id = c.user_profile_id;"
)