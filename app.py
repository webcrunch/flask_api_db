from flask import Flask, render_template, request, jsonify, session
# from flask_cors import CORS
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


# login


@app.route("/api/login", methods=["POST"])
def login():
    conn = mariadb.connect(
        host='database',
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
    cur.execute(
        "SELECT user from items where id = ?", ([request.json['auktion_id']]))
    userId = cur.fetchone()
    if userId is None:
        return jsonify({"data": "there is no item with that id"})
    else:
        for id in userId:
            userId = id

    if userId is session.get('user')[0]:
        return jsonify({"data": "cant bid on your own auction items"})
    # execute a SQL statement
    cur.execute(
        "SELECT amount FROM bids JOIN items ON bids.auction_object = ? ORDER BY amount DESC LIMIT 1", ([request.json['auktion_id']]))
    data = cur.fetchone()
    amount = request.json['amount']

    if (len(data) == 0):
        highest_amount = 0
    else:
        highest_amount = data[0]
    print(highest_amount)
    if (amount > highest_amount):
        cur.execute(
            "INSERT INTO bids (amount,auction_object,time) VALUES (?,?,?)", (
                amount, request.json['auktion_id'], datetime.datetime.now()))
        conn.commit()
        cur.close()
        return jsonify({"data": "new bid placed"})
    else:
        cur.close()
        return jsonify({"data": "there are higher or equal bids"})


@ app.route('/api/items', methods=['GET'])
def getAllAuktionItems():
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
    return jsonify(items)


@app.route('/api/items/own')
def getOwnItems():

    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    print(session.get('user')[0])
    # create a connection cursor
    cur = conn.cursor(dictionary=True)
    # execute a SQL statement
    cur.execute("""SELECT
                items.id,items.title,items.user, items.short_text
                FROM items
                WHERE items.user = ?
                """, ([session.get('user')[0]]))

    items = cur.fetchall()
    for item in items:
        print(item)
    cur.close()
    return jsonify(items)


@ app.route('/api/items/category/<category>', methods=['GET'])
def getAllAuktionItemsFromCategory(category):
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
                items.title, items.category, items.short_text, MAX(amount) AS current_bid
                FROM bids
                RIGHT JOIN
                items
                ON
                bids.auction_object=items.id
                WHERE items.category=?
                GROUP BY auction_object;
                """, ([category]))

    items = cur.fetchall()
    for item in items:
        print(item)
    cur.close()
    return jsonify(items)


@ app.route('/api/items/<item_id>', methods=['GET'])
def getSingleItem(item_id):
    conn = mariadb.connect(
        host='localhost',
        port=3307,
        user='root',
        password='S3cret',
        database='auctionista')

    # create a connection cursor
    cur = conn.cursor(dictionary=True)
    # execute a SQL statement
    cur.execute("SELECT items.id,title,description,start_time,termination_time,starting_price FROM items WHERE items.id = ?",
                [item_id])
    itemObject = cur.fetchall()
    print(itemObject)
    cur.execute("SELECT * FROM images WHERE images.auction_object = ?",
                [item_id])
    imageObject = cur.fetchone()
    cur.execute("SELECT id,amount,time FROM bids WHERE auction_object = ? LIMIT 5",
                [item_id])
    bidObject = cur.fetchall()
    print(type(itemObject))
    cur.close()
    if (len(itemObject) < 1):
        return jsonify({"status": "no items with that identification"})
    return jsonify({"item": itemObject, "images": imageObject,  "bids": bidObject})


@ app.route('/api/items', methods=['POST'])
def insertItems():

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


@app.route('/api/users', methods=['POST'])
def insertUsers():
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
