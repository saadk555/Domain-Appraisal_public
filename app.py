from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify

import process, api
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/generate', methods=['POST'])
def handle_data():
    data = request.get_json()  # get data from POST request
    result = process.my_function(data)  # pass data to function from process.py
    return jsonify(result), 200  # return result as JSON


if __name__ == '__main__':
    app.run(debug=True)