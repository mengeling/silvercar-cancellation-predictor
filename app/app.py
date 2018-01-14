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


@app.route('/new-reservation/', methods=['GET', 'POST'])
def new_reservation():
    if request.method == 'POST':
        # probability = request.form['text']
        probability = 0.8
        return render_template('new_reservation.html', probability=probability, prediction=None)
    # text = np.array([request.form['text']])
    # probability = model.predict_proba(text)[0]
    # prediction = probability > C.THRESHOLD
    return render_template('new_reservation.html', probability=None, prediction=None)


@app.route('/get_subset/', methods=['GET'])
def get_subset():
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


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    with open('../model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    df = pd.read_sql_query("SELECT * FROM booked", con=engine)
    app.run(host='0.0.0.0', port=8080, debug=True)
