import datetime
from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *
from db_app.user_app.user_app import serialize_user_email
import db_app.forum_app.forum_app

app = Blueprint('thread_app', __name__)


def serialize_unicode_thread(thread, thread_id):
    resp = {
        'date': thread[4],
        'dislikes': thread[8],
        'forum': thread[0],
        'id': int(thread_id),
        'isClosed': bool(thread[2]),
        'isDeleted': bool(thread[7]),
        'likes': thread[9],
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


def serialize_thread(thread, user_info, forum_info):
    resp = {
        'date': datetime.datetime.strftime(thread[5], "%Y-%m-%d %H:%M:%S"),
        'dislikes': thread[9],
        'forum': forum_info,
        'id': thread[0],
        'isClosed': bool(thread[3]),
        'isDeleted': bool(thread[8]),
        'likes': thread[10],
        'message': thread[6],
        'slug': thread[7],
        'title': thread[2],
        'user': user_info
    }
    return resp


def serialize_forum1(name):
    select_stmt = ('SELECT * FROM Forums WHERE slug = %s')
    forum = execute_select(select_stmt, name)
    if (forum):
        return db_app.forum_app.forum_app.serialize_forum(forum[0])
    return name


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
    thread_id = execute_insert(insert_stmt, res)
    res.append(0)
    res.append(0)
    answer = jsonify({"code": 0, "response": serialize_unicode_thread(res, thread_id)})
    return answer


@app.route('/details/', methods=['GET'])
def details():
    data = []
    try:
        data.append(request.args.get('thread'))
        select_stmt = ('SELECT * FROM Threads WHERE id = %s')
        print('DEtaaaails')
        print(data[0])
        thread = execute_select(select_stmt, data[0])
        print('DAAAAAAAA')
        print(thread)
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    except Exception:
        answer = {"code": 1, "response": "incorrect related"}
        return jsonify(answer)
    list = request.args.getlist('related')
    user_info = thread[0][4]
    forum_info = thread[0][1]
    print(user_info)
    for related in list:
        if related == 'user':
            user_info = serialize_user_email(thread[0][4])
        if related == 'forum':
            forum_info = serialize_forum1(thread[0][1])
    print(serialize_thread(thread[0], user_info, forum_info))
    answer = jsonify({"code": 0, "response": serialize_thread(thread[0], user_info, forum_info)})
    return answer