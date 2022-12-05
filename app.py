from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import mariadb
import os

app = Flask(__name__)
CORS(app)
resources = {r"/api/*": {"origins": "*"}}
app.config["CORS_HEADERS"] = "Content-Type"
app.config['JSON_SORT_KEYS'] = False


conn = mariadb.connect(
    host='localhost',
    port=3307,
    user='OL_user',
    password='mauFJcuf5dhRMQrjj',
    database='main')


@app.route('/')
def home():
    return jsonify({"Message": "This is your flask app with docker"})


@app.route('/user/<username>')
def show_user(username):
    # Greet the user
    return f'Hello {username} !'


# Items - Auction Objects
@app.route('/api/items', methods=['GET'])
def getAllAuktionItems():
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute("select id,title,short_text from users")
    return jsonify(cur.fetchall())


@app.route('/api/items/<item_id>', methods=['GET'])
def getSingleItem(item_id):
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute("SELECT * FROM users WHERE id = ?",
                [item_id])
    return jsonify(cur.fetchall())

# Users


@app.route('/api/users', methods=['POST'])
def insertUsers():
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute("select * from users WHERE email = ?",
                ([request.json['email']]))
    user = cur.fetchone()
    if (user is None):
        cur.execute(
            "INSERT INTO users (email,password,username,first_name,last_name) VALUES (?, ?,?,?,?)",
            (request.json['email'], request.json['password'], request.json['username'], request.json['first_name'], request.json['last_name']))
        conn.commit()
        return jsonify({"Message": "ID: was inserted"})
    else:
        return jsonify({"data": "user already exist with that email"})


@app.route('/test')
def stina():
    return jsonify(os.environ['MY_USER'])


@app.route('/home')
def hello():
    return render_template('index.html', content="Testing")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7007)
