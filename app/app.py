from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd
import sys
sys.path.append('..')
from model.build_model import get_data

app = Flask(__name__)


with open('../model/model.pkl', 'rb') as f:
    model = pickle.load(f)
df = get_data().sample(30)
temp_df = df.drop(['user_id', 'current_state'], axis=1)
X = pd.get_dummies(temp_df).values
df["predictions"] = model.predict(X)
df["probabilities"] = model.predict_proba(X)[:, 1]
sum_preds = int(np.sum(df["predictions"]))


@app.route('/')
def index():
    return render_template('index.html', data=df.to_html(index=False), res_count=len(df), res_cancel=sum_preds)


@app.route('/submit', methods=['POST'])
def submit():
    text = np.array([request.form['text']])
    prediction = model.predict(text)[0]
    return render_template('submit.html', prediction=prediction)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
