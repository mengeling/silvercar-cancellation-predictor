from flask import Flask, request, render_template
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
    df = pd.read_sql_query("SELECT * FROM booked", con=engine)

    return render_template('index.html', data=df.to_html(index=False), res_count=len(df),
                           res_cancel=df["predictions"].sum())


@app.route('/submit', methods=['POST'])
def submit():
    text = np.array([request.form['text']])
    prediction = model.predict(text)[0]
    return render_template('submit.html', prediction=prediction)


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    with open('../model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    app.run(host='0.0.0.0', port=8080, debug=True)
