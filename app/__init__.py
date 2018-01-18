from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
import pandas as pd
import sys
from sqlalchemy import create_engine

sys.path.append('../model')
import constants as C

app = Flask(__name__)


@app.route('/')
def index():
    """
    Renders index.html template for the main page of the app, using entire booked DataFrame
    """
    total_count = df.shape[0]
    cancellations = df["Cancellation Probability"] > C.THRESHOLD
    cancel_count = np.sum(cancellations.astype(int))
    return render_template(
        'index.html', data=df.drop(["month", "name"], axis=1).to_html(index=False),
        locations=np.sort(df["name"].unique()), months=df["month"].unique(),
        revenue="${:,}".format(int(df[~cancellations]["Price"].sum())), total_count="{:,}".format(total_count),
        cancel_count="{:,}".format(cancel_count), percent_cancelled="{:,.0f}%".format(100 * cancel_count / total_count)
    )


@app.route('/new-reservation/')
def new_reservation():
    """
    Renders new_reservation.html for the interactive demo.
    """
    return render_template('new_reservation.html', locations=np.sort(df["name"].unique()))


@app.route('/get_df_subset/', methods=['GET'])
def get_df_subset():
    """
    Returns smaller DataFrame for the index.html page based off of the month and location drop-down selections.
    """
    location = request.args.get('location', None)
    month = request.args.get('month', None)
    if location is not None and month is not None:
        df_subset = df if location == "All" else df[df["name"] == location]
        df_subset = df_subset if month == "All" else df_subset[df_subset["month"] == month]
        total_count = df_subset.shape[0]
        cancellations = df_subset["Cancellation Probability"] > C.THRESHOLD
        cancel_count = np.sum(cancellations.astype(int))
        return jsonify({
                "location": location,
                "total_count": "{:,}".format(total_count),
                "cancel_count": "{:,}".format(cancel_count),
                "percent_cancelled":  "{:,.0f}%".format(100 * cancel_count / total_count),
                "revenue": "${:,.0f}".format(df_subset[cancellations]["Price"].sum()),
                "data": df_subset.drop(["month", "name"], axis=1).to_html(index=False)
        })


@app.route('/calculate_probability/', methods=['GET'])
def calculate_probability():
    """
    Creates a DataFrame with one row based off of the inputs to then calculate
    the probability and prediction for the interactive demo.
    """
    df_new = pd.DataFrame(request.args, index=[0])
    X = model.pipeline.transform_individual(df_new)
    probability = model.classifier.predict_proba(X)[0, 1]
    prediction = "Cancelled Ride" if probability > C.THRESHOLD else "Finished Ride"
    price = 0 if df_new["dropoff"].values < df_new["pickup"].values else int(
        50 * (pd.to_datetime(df_new["dropoff"]) - pd.to_datetime(df_new["pickup"])).dt.total_seconds() / 86400
    )
    return jsonify({
        "probability": "{:,.2f}".format(probability),
        "prediction": prediction,
        "price": "${:,.0f}".format(price)
    })


if __name__ == '__main__':
    # Load model from pickle file and then retrieve the booked data
    with open('../model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    engine = create_engine(C.ENGINE)
    df = pd.read_sql_query("SELECT * FROM booked", con=engine)
    df.sort_values("probability", inplace=True, ascending=False)
    df.rename(index=str, columns=C.APP_COL_NAMES, inplace=True)
    app.run(debug=True)
