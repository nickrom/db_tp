from flask import jsonify, Blueprint
from flask import request
from db_app.executor import *
import urlparse

app = Blueprint('user_app', __name__)

def serialize_user_email(email_user):
    select_stmt = ('SELECT * FROM Users WHERE email = %s')
    user = execute_select(select_stmt, email_user)
    user = user[0]
    return serialize_user(user, get_subscriptions(user), get_followers(user), get_following(user))


def serialize_user_id(res):
    resp = { 'about': res[1],
        'email': res[3],
        'id': res[5],
        'isAnonymous': bool(res[4]),
        'name': res[2],
        'username': res[0]
    }
    return resp


def get_subscriptions(user):
    return []


def get_followers(user):
    return []


def get_following(user):
    return []


def serialize_user(user, subscriptions, followers, following):
    resp = { 'about': user[2],
        'email': user[4],
        'followers': followers,
        'following': following,
        'id': user[0],
        'isAnonymous': bool(user[5]),
        'name': user[3],
        'subscriptions': subscriptions,
        'username': user[1]
    }
    return resp


def __parse_user_request_data(json_data):
    res = []
    try:
        res.append((json_data["username"]))
        res.append((json_data["about"]))
        res.append((json_data["name"]))
        res.append((json_data["email"]))
        try:
            res.append((json_data["isAnonymous"]))
        except KeyError:
            res.append(0)
            pass
    except KeyError:
        res = []
    return res


@app.route('/create/', methods=['POST'])
def create():
    user_data = request.json
    res = __parse_user_request_data(user_data)
    if(len(res) == 0):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE email = %s')
    usr = execute_select(select_stmt, res[3])
    if(len(usr) != 0):
        answer = {"code": 5, "response": "User already exists"}
        return jsonify(answer)
    insert_stmt = (
        'INSERT INTO Users (username, about, name, email, isAnonymous) '
        'VALUES (%s, %s, %s, %s, %s)'
    )
    user_id = execute_insert(insert_stmt, res)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE id = %s')
    resp = execute_select(select_stmt, user_id)
    res.append(resp[0][0])
    answer = jsonify({"code": 0, "response": serialize_user_id(res)})
    return answer






