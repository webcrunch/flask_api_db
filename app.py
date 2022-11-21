from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json


app = Flask(__name__)
CORS(app)
resources = {r"/api/*": {"origins": "*"}}
app.config["CORS_HEADERS"] = "Content-Type"
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def home():
    return jsonify({"Message": "This is your flask app with docker"})


@app.route('/user/<username>')
def show_user(username):
    # Greet the user
    return f'Hello {username} !'


@app.route('/home')
def hello():
    return render_template('index.html', content="Testing")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7007)
