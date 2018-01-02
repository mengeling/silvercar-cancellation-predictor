from flask import Flask, request, render_template
import pickle
import numpy as np
import sys
sys.path.append('..')
from model.build_model import clean_data

app = Flask(__name__)


with open('data/model.pkl', 'rb') as f:
    model = pickle.load(f)
df = clean_data(sample=True)
df.pop("current_state")
probs = model.predict_proba(df.values)
print(probs)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    text = np.array([request.form['text']])
    prediction = model.predict(text)[0]
    return render_template('submit.html', prediction=prediction)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
