from flask_cors import CORS
from datetime import datetime
from flask_socketio import SocketIO

from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, jsonify, request, make_response
import ssl

app = Flask(__name__)
app.config["SECRET_KEY"] = '88024e1b4d3d7a4d7c2f839092334feb1d4c8c36'
socket_io = SocketIO(app, cors_allowed_origins="*")
CORS(app)
app.config['JSON_AS_ASCII'] = False


to_id = "5fc23d1346ea132fe3066973"
from_id = "5fc2387539dc49f806f755c5"

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


db = connect_to_database()
date = datetime.now()
print(date)


def get_correspondents(from_id):
    cursor = db.user.find({"from_id": from_id})
    result = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        result.append(item)
    return jsonify({'result': result})


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
    cursor = db.user.find({"login": query})
    for item in cursor:
        id = str(item["_id"])
    return id


@app.route("/messages")
def get_messages_from_chat():
    '''data = request.get_json()
    from_id = data['from_id']
    to_id = data['to_id']'''
    cursor = db.message.find(
        {"$or": [
            {"to_id": from_id, "from_id": to_id},
            {"to_id": to_id, "from_id": from_id}
        ]
        })
    result = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        result.append(item)
    return jsonify(result)


@app.route("/send", methods=['POST'])
def send_message():
    data = request.get_json()
    from_id = data['from_id']
    to_id = data['to_id']
    text = data['text']
    date = datetime.now()
    db.message.insert_one(
        {"from_id": from_id, "to_id": to_id, "text": text, "date": date})
    #socket_io.emit('message', get_messages_from_chat(to_id, from_id))
    return {'response': 'ok'}



app.run()
