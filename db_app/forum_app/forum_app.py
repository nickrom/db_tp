from flask import Blueprint, request, jsonify
from db_app.executor import *
import urlparse
from db_app.thread_app.thread_app import serialize_thread
from db_app.user_app.user_app import serialize_user_email

app = Blueprint('forum_app', __name__)


def serialize_forum(forum):
    json = {
        'id': forum[0],
        'name': forum[1],
        'short_name': forum[2],
        'user': forum[3]
    }
    return json


def serialize_forum_user(forum, user):
    json = {
        'id': forum[0],
        'name': forum[1],
        'short_name': forum[2],
        'user': user
    }
    return json

def serialize_post(post):
    resp = {
        'date': post[1],
        'forum': post[5],
        'id': post[0],
        'isApproved': bool(post[7]),
        'isDeleted': bool(post[11]),
        'isEdited': bool(post[9]),
        'isHighlighted': bool(post[8]),
        'isSpam': bool(post[10]),
        'message': post[3],
        'parent': post[6],
        'thread': post[2],
        'user': post[4]
    }
    return resp


@app.route('/create/', methods=['POST'])
def create():
    data = request.json
    forum_data = []
    try:
        forum_data.append(data["name"])
        forum_data.append(data["short_name"])
        forum_data.append(data["user"])
        insert_stmt = ('INSERT INTO Forums (name, slug, user) VALUES (%s, %s, %s)')
        id = execute_insert(insert_stmt, forum_data)
        forum_data.insert(0,id)
        forum = serialize_forum(forum_data)
        answer = {"code": 0, "response": forum}
    except (KeyError,Exception):
        answer = {"code": 2, "response": "invalid json"}
    return jsonify(answer)


@app.route('/details/', methods=['GET'])
def details():
    data = []
    try:
        data.append(request.args.get('forum'))
        select_stmt = ('SELECT * FROM Forums WHERE slug = %s')
        forum = execute_select(select_stmt, data[0])
    except KeyError:
        print(data)
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    except Exception:
        answer = {"code": 1, "response": "incorrect related"}
        return jsonify(answer)
    if request.args.get('related') == 'user':
        user_info = serialize_user_email(forum[0][3])
        answer = {"code": 0, "response": serialize_forum_user(forum[0], user_info)}
        print(answer)
        return jsonify(answer)
    answer = {"code": 0, "response": serialize_forum(forum[0])}
    return jsonify(answer)