from flask import Flask, render_template, request, jsonify, session
# from flask_cors import CORS
import json
import mariadb
import os

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


# get current user
@app.route("/api/user", methods=["GET"])
def user_data():
    if session.get('user'):
        return jsonify(session['user'])

    return jsonify({"login": False})


@app.route('/')
def home():
    return jsonify({"Message": "This is your flask app with docker"})


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
