
from flask import Flask, render_template, request, jsonify, session
# from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

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

# flask swagger configs
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')

API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Auctionista "
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT)


# if os.environ['FLASK_PORT'] is None:
#     flask_port = 7007
# else:
#     flask_port = os.environ['FLASK_PORT']

# print(flask_port)
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
    if user is None:
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
def insert_bids():
    if session.get('user') is None:
        return jsonify({"error": "Need to be logged in to see this"})
    else:
        # get the highest bid amount
        conn = mariadb.connect(
            host='localhost',
            port=3307,
            user='root',
            password='S3cret',
            database='auctionista')
        # create a connection cursor
        cur = conn.cursor()
        cur.execute(
            "SELECT user from items where id = ?", ([request.json['auction_id']]))
        user_id = cur.fetchone()
        print(user_id)
        if user_id is None:
            return jsonify({"data": "there is no item with that id"})
        else:
            for id in user_id:
                user_id = id

        if user_id is session.get('user')["id"]:
            return jsonify({"data": "cant bid on your own auction items"})
        # execute a SQL statement
        cur.execute(
            "SELECT amount FROM bids JOIN items ON bids.auction_object = ? ORDER BY amount DESC LIMIT 1",
            ([request.json['auction_id']]))
        data = cur.fetchone()
        amount = request.json['amount']

        if len(data) == 0:
            highest_amount = 0
        else:
            highest_amount = data[0]
        print(highest_amount)
        if amount > highest_amount:
            cur.execute(
                "INSERT INTO bids (amount,auction_object,time) VALUES (?,?,?)", (
                    amount, request.json['auction_id'], datetime.datetime.now()))
            conn.commit()
            cur.close()
            return jsonify({"data": "new bid placed"})
        else:
            cur.close()
            return jsonify({"data": "there are higher or equal bids"})


@app.route('/api/items', methods=['GET'])
def get_all_auction_items():
    #   flask_port = int(os.environ['PORT'])
    #     flask_host = str(os.environ['HOST'])
    #     flask_pass = str(os.environ['MYSQL_PASSWORD'])
    #     flask_user = str(os.environ['MYSQL_USER'])
    # flask_db = str(os.environ['MYSQL_DATABASE'])
    #     print(flask_port, flask_host)

    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor(dictionary=True)
    # execute a SQL statement
    cur.execute("""SELECT items.id,items.user,items.title,items.short_text, MAX(amount) AS current_bid
                    FROM items
                    LEFT JOIN bids
                    ON bids.auction_object = items.id
                    GROUP BY auction_object;
                """)

    items = cur.fetchall()
    cur.close()
    res = jsonify(items)
    res.status_code = 200
    return res


@app.route('/api/items/own', methods=['GET'])
def get_own_items():
    # check if someone is logged in first
    if session.get('user') is None:
        return jsonify({"error": "Need to be logged in to see this"})
    else:
        conn = mariadb.connect(
            host='localhost',
            port=3307,
            user='root',
            password='S3cret',
            database='auctionista')

        print(session.get('user'))
        # create a connection cursor
        cur = conn.cursor(dictionary=True)
        # execute a SQL statement
        cur.execute("""SELECT
                items.id,items.title,items.user, items.short_text
                FROM items
                WHERE items.user = ?
                """, ([session.get('user')[0]]))

        items = cur.fetchall()
        print(items)
        cur.close()
        return jsonify(items)


@app.route('/api/items/category/<category>', methods=['GET'])
def get_all_auction_items_from_category(category):
    print(category)
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor(dictionary=True)
    # execute a SQL statement
    cur.execute("""SELECT
                items.id,items.title,items.user, items.short_text
                FROM items
                WHERE items.category = ?
                """, ([category]))
    items = cur.fetchall()
    cur.close()
    return jsonify(items)


@app.route('/api/items/<item_id>', methods=['GET'])
def get_single_item(item_id):
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor(dictionary=True)
    # execute a SQL statement
    cur.execute(
        "SELECT items.id,title,description,start_time,termination_time,starting_price FROM items WHERE items.id = ?",
        [item_id])
    item_object = cur.fetchall()
    cur.execute("SELECT * FROM images WHERE images.auction_object = ?",
                [item_id])
    image_object = cur.fetchone()
    cur.execute("SELECT id,amount,time FROM bids WHERE auction_object = ? LIMIT 5",
                [item_id])
    bid_object = cur.fetchall()
    cur.close()
    if len(item_object) < 1:
        return jsonify({"status": "no items with that identification"})
    return jsonify({"item": item_object, "images": image_object, "bids": bid_object})


@app.route('/api/items', methods=['POST'])
def insert_items():
    if session.get('user') is None:
        return jsonify({"error": "Need to be logged in to see this"})
    else:
        conn = mariadb.connect(
            host='localhost',
            port=3307,
            user='root',
            password='S3cret',
            database='auctionista')

        # create a connection cursor
        cur = conn.cursor(dictionary=True)
        # execute a SQL statement
        cur.execute(
            """INSERT INTO items 
            ( 
            title,
            short_text, 
            description,
            start_time,
            termination_time,
            starting_price,
            category,
            user
            ) VALUES (?,?,?,?,?,?,?,?)""",
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


@app.route('/api/users', methods=['POST'])
def insert_users():
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor(dictionary=True)
    # execute a SQL statement
    cur.execute("select * from users WHERE email = ?",
                ([request.json['email']]))
    user = cur.fetchone()
    if user is None:
        cur.execute(
            "INSERT INTO users (email,password,username,first_name,last_name) VALUES (?, ?,?,?,?)",
            (request.json['email'], request.json['password'], request.json['username'], request.json['first_name'],
             request.json['last_name']))
        conn.commit()
        cur.close()
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
