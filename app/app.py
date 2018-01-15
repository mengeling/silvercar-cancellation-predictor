from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
import pandas as pd
import sys
from sqlalchemy import create_engine

sys.path.append('../model')
from model import CancellationModel
import constants as C

app = Flask(__name__)


@app.route('/')
def index():
    return render_template(
        'index.html', data=df.to_html(index=False), locations=np.sort(df["name"].unique()),
        months=df["month"].unique(), revenue="${:,}".format(int(df[df["prediction"] == 0]["price"].sum())),
        total_count="{:,}".format(len(df)), cancel_count="{:,}".format(df["prediction"].sum())
    )


@app.route('/new-reservation/')
def new_reservation():
    return render_template('new_reservation.html', locations=np.sort(df["name"].unique()))


@app.route('/get_df_subset/', methods=['GET'])
def get_df_subset():
    location = request.args.get('location', None)
    month = request.args.get('month', None)
    if location is not None and month is not None:
        df_subset = df if location == "All" else df[df["name"] == location]
        df_subset = df_subset if month == "All" else df_subset[df_subset["month"] == month]
        d = {
            "location": location,
            "total_count": "{:,}".format(df_subset.shape[0]),
            "cancel_count": "{:,}".format(df_subset["prediction"].sum()),
            "revenue": "${:,.0f}".format(df_subset[df_subset["prediction"] == 0]["price"].sum()),
            "data": df_subset.to_html(index=False)
        }
        return jsonify(d)


@app.route('/calculate_probability/', methods=['GET'])
def calculate_probability():
    df_new = pd.DataFrame(request.args, index=[0])
    df_new = df_new.apply(pd.to_numeric, errors='ignore')
    df_new["past_percent_cancelled"] = df_new["past_cancellations"] / df_new["past_rides"]\
        if df_new["past_rides"].sum() != 0 else 0.41
    time_zone = df[df["name"] == df_new["location"].iloc[0]]["time_zone"].iloc[0]
    df_new["western_pickup"] = (time_zone == "pst") | (time_zone == "mst")
    df_new["insurance_corporate"] = df_new["insurance"].iloc[0] == "Corporate"
    df_new["insurance_personal"] = df_new["insurance"].iloc[0] == "Personal"
    df_new["insurance_silvercar"] = df_new["insurance"].iloc[0] == "Silvercar"
    df_new["created_at"] = pd.to_datetime(df_new["created_at"])
    df_new["pickup"] = pd.to_datetime(df_new["pickup"])
    df_new["dropoff"] = pd.to_datetime(df_new["dropoff"])
    df_new["days_to_pickup"] = (df_new["pickup"] - df_new["created_at"]).dt.total_seconds() / 86400
    df_new["trip_duration"] = (df_new["dropoff"] - df_new["pickup"]).dt.total_seconds() / 86400
    df_new["weekend_pickup"] = df_new["pickup"].dt.dayofweek.isin([4, 5, 6])
    df_new["winter_pickup"] = df_new["pickup"].dt.month.isin([1, 12])
    df_new.replace({"Yes": 1, "No": 0, True: 1, False: 0}, inplace=True)
    df_new = df_new[C.FEATURES_TO_KEEP]
    X = model.pipeline.scaler.transform(df_new)
    probability = model.classifier.predict_proba(X)[0, 1]
    prediction = "Cancelled Ride" if probability > C.THRESHOLD else "Finished Ride"
    price = df_new["trip_duration"].iloc[0] * 50
    d = {
        "probability": "{:,.2f}".format(probability),
        "prediction": prediction,
        "price": "${:,.0f}".format(price)
    }
    return jsonify(d)


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    with open('../model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    df = pd.read_sql_query("SELECT * FROM booked", con=engine)
    app.run(host='0.0.0.0', port=8080, debug=True)
