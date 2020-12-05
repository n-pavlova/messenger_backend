# from flask_cors import CORS
from datetime import datetime
from flask_socketio import SocketIO

from bson import ObjectId
from pymongo import MongoClient
from flask import Flask, jsonify, request
import ssl

app = Flask(__name__)
app.config["SECRET_KEY"] = '88024e1b4d3d7a4d7c2f839092334feb1d4c8c36'
socket_io = SocketIO(app, cors_allowed_origins="*")
# CORS(app)
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


db = connect_to_database()



def get_users():
    cursor = db.user.find({})
    result = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        result.append(item)
    return jsonify({'result': result})


@app.route("/auth")
def auth():
    data = request.json
    login = data["login"]
    password = data["password"]

    print(get_password_by_login("natalya"))
    print(get_password_by_login("kur"))

def get_password_by_login(login):
    cursor = db.user.find({"login": login})
    password = None
    for item in cursor:
        password = item["password"]
        break
    if password is None:
        return -1
    return password

def get_messages_from_chat(to_id, from_id):
    cursor = db.user.find({"to_id": ObjectId(to_id), "from_id": ObjectId(from_id)})


@app.route("/send", methods=['POST'])
def send_message(from_id, to_id, text):
    ''', "time": datetime.now'''
    db.message.insert_one({ "from_id": from_id, "to_id": to_id, "text": text})
    socket_io.emit('message', get_messages_from_chat(to_id, from_id))


app.run()
