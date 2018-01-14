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
    return render_template('index.html', data=df.to_html(index=False), location="All", locations=locations,
                           total_count=len(df), cancel_count=df["predictions"].sum())


@app.route('/', methods=['GET', 'POST'])
def reservations():
    if request.method == "POST":
        print(request.form, request.args)
        location = request.form.get("locations", None)
        print(location)
        if location is not None:
            df_location = df if location == "All" else df[df["name"] == location]
            return render_template(
                'index.html', data=df_location.to_html(index=False), location=location, locations=locations,
                res_count=len(df_location), res_cancel=df_location["predictions"].sum()
            )
    # df_location = df[df["name"] == location]
    # print(df_location.head())
    # return render_template('show_reservations.html',
    #                        data=df_location.to_html(index=False), locations=np.sort(df["name"].unique()),
    #                        res_count=len(df), res_cancel=df["predictions"].sum())


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


@app.route('/location_subset/', methods=['GET'])
def location_subset():
    location = request.args.get('location', None)
    if location is not None:
        df_location = df if location == "All" else df[df["name"] == location]
        d = {
            "location": location,
            "total_count": len(df_location),
            "cancel_count": df_location["predictions"].sum(),
            "data": df_location.to_html(index=False)
        }
        return jsonify(d)


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    with open('../model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    df = pd.read_sql_query("SELECT * FROM booked", con=engine)
    locations = np.sort(df["name"].unique())
    app.run(host='0.0.0.0', port=8080, debug=True)
