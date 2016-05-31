from flask import Blueprint, request, jsonify
from db_app.executor import *

app = Blueprint('forum_app', __name__)


def serialize_forum(forum, forum_id):
    json = {
        'id': forum_id,
        'name': forum[0],
        'short_name': forum[1],
        'user': forum[2]
    }
    return json


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
        forum = serialize_forum(forum_data, id)
        answer = {"code": 0, "response": forum}
    except (KeyError,Exception):
        answer = {"code": 2, "response": "invalid json"}
    return jsonify(answer)

