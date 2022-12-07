from flask import Flask, render_template, request, jsonify, session
# from flask_cors import CORS
import json
import mariadb
import os
import datetime

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY="secret_sauce",
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Strict",
)

# CORS(app)
# resources = {r"/api/*": {"origins": "*"}}
app.config["CORS_HEADERS"] = "Content-Type"
app.config['JSON_SORT_KEYS'] = False

# config = {
#     'host': 'localhost',
#     'port': 3307,
#     'user': 'root',
#     'password': 'S3cret!',
#     'database': 'main'
# }

# login


@app.route("/api/login", methods=["POST"])
def login():
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute("select * from users WHERE email = ? AND password = ?",
                (request.json['email'], request.json['password']))
    user = cur.fetchone()
    if (user is None):
        return jsonify({"login": False})
    else:
        session['user'] = user
        return jsonify({"login": True})

# logout


@app.route("/api/login", methods=["DELETE"])
def logout():
    session['user'] = {}
    return jsonify({"logout": True})

# get current user
@app.route("/api/user", methods=["GET"])
def user_data():
    if session.get('user'):
        return jsonify(session['user'])

    return jsonify({"login": False})


@app.route('/')
def home():
    return jsonify({"Message": "This is your flask app with docker"})


# Bids
@app.route('/api/bids', methods=['POST'])
def insertBids():
    # get the highest bid amount
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute(
        "SELECT amount FROM bids JOIN items ON bids.auction_object = ? ORDER BY amount DESC LIMIT 1", ([request.json['auktion_id']]))
    data = cur.fetchall()
    amount = request.json['amount']

    if (len(data) == 0):
        highest_amount = 0
    else:
        highest_amount = data[0][0]
    if (amount > highest_amount):
        cur.execute(
            "INSERT INTO bids (amount,auction_object,time) VALUES (?,?,?)", (
                amount, request.json['auktion_id'], datetime.datetime.now()))
        conn.commit()
        cur.close()
        return jsonify({"data": "new bid placed"})
    else:
        cur.close()
        return jsonify({"data": "there are higher bids"})


@app.route('/api/bids/current', methods=['GET'])
def getCurrentBids():
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute("SELECT * FROM items")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

# Items - Auction Objects


@ app.route('/api/items', methods=['GET'])
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
    cur.close()
    return jsonify(cur.fetchall())


@ app.route('/api/items/<item_id>', methods=['GET'])
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
    cur.close()
    return jsonify(cur.fetchall())


@ app.route('/api/items', methods=['POST'])
def insertItems():

    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor()
    # execute a SQL statement
    cur.execute(
        "INSERT INTO items (title,short_text, description,start_time,termination_time,starting_price,category,user) VALUES (?,?,?,?,?,?,?,?)",
        (request.json['title'],
         request.json['short_text'],
         request.json['description'],
         request.json["start_time"],
         request.json["termination_time"],
         request.json["starting_price"],
         request.json["category"],
         request.json["user"]))
    conn.commit()
    cur.close()
    return jsonify({"Message": "ID: was inserted"})


# Users
@ app.route('/api/users', methods=['POST'])
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
        cur.close()
        return jsonify({"Message": "ID: was inserted"})
    else:
        return jsonify({"data": "user already exist with that email"})


@ app.route('/test')
def stina():
    return jsonify(os.environ['MY_USER'])


@ app.route('/home')
def hello():
    return render_template('index.html', content="Testing")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7007)
