from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *

app = Blueprint('thread_app', __name__)


def serialize_unicode_thread(thread, thread_id):
    resp = {
        'date': thread[4],
        'forum': thread[0],
        'id': int(thread_id),
        'isClosed': bool(thread[2]),
        'isDeleted': bool(thread[7]),
        'message': thread[5],
        'slug': thread[6],
        'title': thread[1],
        'user': thread[3]
    }
    return resp


def serialize_thread(thread, thread_id):
    resp = {
        'date': thread[4].isoformat(sep=' '),
        'forum': thread[0],
        'id': int(thread_id),
        'isClosed': bool(thread[2]),
        'isDeleted': bool(thread[7]),
        'message': thread[5],
        'posts': thread[8],
        'slug': thread[6],
        'title': thread[1],
        'user': thread[3]
    }
    return resp


def _parse_thread_request_data(json_data):
    res = []
    try:
        res.append((json_data["forum"]))
        res.append((json_data["title"]))
        res.append(int((json_data["isClosed"])))
        res.append((json_data["user"]))
        res.append((json_data["date"]))
        res.append((json_data["message"]))
        res.append((json_data["slug"]))
        try:
            res.append(int((json_data["isDeleted"])))
        except KeyError:
            res.append(0)
            pass
    except KeyError:
        res = []
    return res


@app.route('/create/', methods=['POST'])
def create():
    thread_data = request.json
    res = _parse_thread_request_data(thread_data)
    if(len(res) < 7):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    insert_stmt = ('INSERT INTO Threads (forum, title, isClosed, user, date, message, slug, isDeleted) '
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    )
    user_id = execute_insert(insert_stmt, res)
    answer = jsonify({"code": 0, "response": serialize_unicode_thread(res, user_id)})
    return answer
