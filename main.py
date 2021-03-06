from flask_cors import CORS
from datetime import datetime
from flask_socketio import SocketIO

from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, jsonify, request, make_response
import ssl
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = '88024e1b4d3d7a4d7c2f839092334feb1d4c8c36'
socket_io = SocketIO(app, cors_allowed_origins="*")
CORS(app)
app.config['JSON_AS_ASCII'] = False



@app.route('/')
@app.route('/index')
def main_page():
    get_password_by_login('natalya')
    return 'kurr'


def connect_to_database():
    client = MongoClient(
        "mongodb+srv://vdno:kurluk@cluster0.pdeej.mongodb.net/test?retryWrites=true&w=majority")
    database = client.sysdba
    return database



@app.route("/correspondents", methods=['POST', 'GET'])
def get_correspondents():
    data = request.get_json()
    from_id = data["id"]
    cursor_from = db.message.find({"from_id": from_id}).distinct("to_id")
    result = []
    for item in cursor_from:
        result.append(item)
    cursor_to = db.message.find({"to_id": from_id}).distinct("from_id")
    for item in cursor_to:
        result.append(item)
    result = set(result)
    list_of_users = []
    for item in result:
        list_of_users.append(get_user_by_id(item))
    return jsonify(list_of_users)


def get_user_by_id(id):
    cursor = db.user.find({"_id": ObjectId(id)})
    result = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        return item

@app.route("/auth", methods=['POST'])
def auth():
    data = request.get_json()
    login = data["login"]
    password = data["password"]

    check = get_password_by_login(login)
    if check is None:
        id = create_user(login, password)
        return {'id': id, 'success': true}
    else:
        if password == check:
            id = get_id_by_login(login)
            return jsonify({"id": id, 'success': True})
        else:
            return jsonify({'success': False})



def get_password_by_login(login):
    cursor = db.user.find({"login": login})
    password = None
    for item in cursor:
        password = item["password"]
        break
    if password is None:
        return None
    return password

def get_id_by_login(login):
    cursor = db.user.find({"login": login})
    for item in cursor:
        return str(item["_id"])
    return None

def create_user(login, password):
    id = db.user.insert_one(
        {"login": login, "password": password})
    return str(id.inserted_id)


@app.route("/search")
def search():
    data = request.get_json()
    query = data['query']
    rgx = re.compile('.*' + query +'.*', re.IGNORECASE)  # compile the regex
    cursor = db.user.find({"login":rgx})
    result = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        result.append(item)
    return jsonify(result)


@app.route("/messages", methods=['POST', 'GET'])
def get_messages_from_chat():
    s = request
    data = request.get_json()
    from_id = data['from_id']
    to_id = data['to_id']
    cursor = db.message.find(
        {"$or": [
            {"to_id": from_id, "from_id": to_id},
            {"to_id": to_id, "from_id": from_id}
        ]
        }).sort([("date", 1)])
    result = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        result.append(item)
    return jsonify(result)


@app.route("/send", methods=['POST'])
def send_message():
    data = request.get_json()
    from_id = data['from_id']
    to_id = data['to_id']['_id']
    text = data['text']
    date = datetime.now()
    db.message.insert_one(
        {"from_id": from_id, "to_id": to_id, "text": text, "date": date})
    return {'success': 'ok'}


db = connect_to_database()
app.run()
