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
        return jsonify(
            {"location": location,
            "total_count": "{:,}".format(df_subset.shape[0]),
            "cancel_count": "{:,}".format(df_subset["prediction"].sum()),
            "revenue": "${:,.0f}".format(df_subset[df_subset["prediction"] == 0]["price"].sum()),
            "data": df_subset.to_html(index=False)}
        )


@app.route('/calculate_probability/', methods=['GET'])
def calculate_probability():
    df_new = pd.DataFrame(request.args, index=[0])
    X = model.pipeline.transform_individual(df_new)
    probability = model.classifier.predict_proba(X)[0, 1]
    prediction = "Cancelled Ride" if probability > C.THRESHOLD else "Finished Ride"
    return jsonify(
        {"probability": "{:,.2f}".format(probability),
        "prediction": prediction}
    )


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    with open('../model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    df = pd.read_sql_query("SELECT * FROM booked", con=engine)
    app.run(host='0.0.0.0', port=8080, debug=True)
