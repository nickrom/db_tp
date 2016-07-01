from flask import Blueprint
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
from db_app.executor import *
import urlparse
import db_app.forum_app.forum_app
import db_app.thread_app.thread_app
from db_app.user_app.user_app import serialize_user_email

app = Blueprint('post_app', __name__)


def posts_to_list(posts):
    resp = []
    for post in posts:
        resp.append(serialize_post1(post[1:], post[0]))
    return resp


def serialize_unicode_post(post, post_id):
    resp = {
        'date': post[0],
        'forum': post[4],
        'id': post_id,
        'isApproved': bool(post[6]),
        'isDeleted': bool(post[10]),
        'isEdited': bool(post[8]),
        'isHighlighted': bool(post[7]),
        'isSpam': bool(post[9]),
        'message': post[2],
        'parent': post[5],
        'thread': post[1],
        'user': post[3]
    }
    return resp


def serialize_post1(post, post_id):
    resp = {
        'date': post[0].isoformat(sep=' '),
        'dislikes': post[11],
        'forum': post[4],
        'id': post_id,
        'isApproved': bool(post[6]),
        'isDeleted': bool(post[10]),
        'isEdited': bool(post[8]),
        'isHighlighted': bool(post[7]),
        'isSpam': bool(post[9]),
        'likes': post[12],
        'message': post[2],
        'parent': post[5],
        'points': post[13],
        'thread': post[1],
        'user': post[3]
    }
    return resp


def serialize_post(post, user_info, forum_info, thread_info):
    resp = {
        'date': post[1].isoformat(sep=' '),
        'dislikes': post[12],
        'forum': forum_info,
        'id': post[0],
        'isApproved': bool(post[7]),
        'isDeleted': bool(post[11]),
        'isEdited': bool(post[9]),
        'isHighlighted': bool(post[8]),
        'isSpam': bool(post[10]),
        'likes': post[13],
        'message': post[3],
        'parent': post[6],
        'points': post[14],
        'thread': thread_info,
        'user': user_info
    }
    return resp


def parse_post_data(data):
    res = []
    try:
        res.append(data["date"])
        res.append(data["thread"])
        res.append(data["message"])
        res.append(data["user"])
        res.append(data["forum"])
    except KeyError:
        res = []
    return res


@app.route('/create/', methods=['POST'])
def create():
    try:
        post_data = request.json
    except BadRequest:
        return jsonify(code=2, response="Cant parse json")
    data = parse_post_data(post_data)
    if(len(data) < 5):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    optional = [None, 0, 0, 0, 0, 0]
    for el in optional:
        data.append(el)
    try:
        parent_id = post_data["parent"]
        data[5] = parent_id
    except KeyError:
        pass
    try:
        data[6] = int(post_data["isApproved"])
    except KeyError:
        pass
    try:
        data[7] = int(post_data["isHighlighted"])
    except KeyError:
        pass
    try:
        data[8] = int(post_data["isEdited"])
    except KeyError:
        pass
    try:
        data[9] = int(post_data["isSpam"])
    except KeyError:
        pass
    try:
        data[10] = int(post_data["isDeleted"])
    except KeyError:
        pass
    insert_stmt = ('INSERT INTO Posts (date, thread, message, user, forum, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted)'
                   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    )
    inserted_id = execute_insert(insert_stmt, data)
    upd_stmt = ('UPDATE Threads SET posts = posts + 1 WHERE id = %s')
    execute_insert(upd_stmt, [int(data[1])])
    post = serialize_unicode_post(data, inserted_id)
    answer = {"code": 0, "response": post}
    return jsonify(answer)


def serialize_thread1(name):
    select_stmt = ('SELECT * FROM Threads WHERE id = %s')
    thread = execute_select(select_stmt, name)
    if (thread):
        return db_app.thread_app.thread_app.serialize_thread(thread[0], thread[0][4], thread[0][1])
    return name


@app.route('/details/', methods=['GET'])
def details():
    data = []
    try:
        data.append(request.args.get('post'))
        select_stmt = ('SELECT * FROM Posts WHERE id = %s')
        if (int(data[0])<0):
            return jsonify({"code": 1, "response": "object not found"})
        post = execute_select(select_stmt, data[0])
        if (post):
            pass
        else:
            return jsonify({"code": 1, "response": "object not found"})
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    except Exception:
        answer = {"code": 1, "response": "incorrect related"}
        return jsonify(answer)
    list = request.args.getlist('related')
    user_info = post[0][4]
    forum_info = post[0][5]
    thread_info = post[0][2]
    for related in list:
        if related == 'user':
            user_info = db_app.user_app.user_app.serialize_user_email(post[0][4])
        if related == 'forum':
            forum_info = db_app.thread_app.thread_app.serialize_forum1(post[0][5])
        if related == 'thread':
            thread_info = serialize_thread1(post[0][2])
    answer = jsonify({"code": 0, "response": serialize_post(post[0], user_info, forum_info, thread_info)})
    return answer


@app.route('/list/', methods=['GET'])
def list():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    limit = 0
    forum = 0
    try:
        data.append(int(req["thread"][0]))
        select_stmt = ('SELECT * FROM Posts WHERE thread = %s')
    except KeyError:
        try:
            data.append(req["forum"][0])
            select_stmt = ('SELECT * FROM Posts WHERE forum = %s')
            forum = 1
        except KeyError:
            answer = {"code": 3, "response": "incorrect request"}
            return jsonify(answer)
    try:
        data.append(req["since"][0])
        select_stmt += ' AND date > %s '
    except KeyError:
        pass
    try:
        #data.append(req["order"])
        select_stmt += ' ORDER BY date ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY date ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s '
        limit = 1
    except KeyError:
        pass
    posts = execute_select(select_stmt, tuple(data))
    resp = posts_to_list(posts)
    answer = {"code": 0, "response": resp}
    return jsonify(answer)


@app.route('/remove/', methods=['POST'])
def remove():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Posts SET isDeleted = 1 WHERE id = %s')
    execute_insert(upd_stmt, rem_data)
    upd_stmt = 'UPDATE Threads as t LEFT JOIN Posts as p ON p.thread=t.id SET t.posts = t.posts - 1 WHERE p.id = %s '
    execute_insert(upd_stmt, rem_data)
    answer = {"code": 0, "response": {"post": rem_data[0]}}
    return jsonify(answer)


@app.route('/restore/', methods=['POST'])
def restore():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Posts SET isDeleted = 0 WHERE id = %s')
    execute_insert(upd_stmt, rem_data)
    upd_stmt = 'UPDATE Threads as t LEFT JOIN Posts as p ON p.thread=t.id SET t.posts = t.posts + 1 WHERE p.id = %s '
    execute_insert(upd_stmt, rem_data)
    answer = {"code": 0, "response": {"post": rem_data[0]}}
    return jsonify(answer)


@app.route('/update/', methods=['POST'])
def update():
    data = request.json
    up_data = []
    try:
        up_data.append(data["message"])
        up_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Posts SET message = %s WHERE id = %s')
    ins_id = execute_insert(update_stmt, up_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)


@app.route('/vote/', methods=['POST'])
def vote():
    data = request.json
    vote_data = []
    upd_stmt = ()
    upd_points = ()
    try:
        vote_data.append(data["vote"])
        vote_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    if(vote_data[0] == 1):
        upd_stmt = 'UPDATE Posts SET likes = likes + 1, points = points + 1 WHERE id = %s'
    if(vote_data[0] == -1):
        upd_stmt = 'UPDATE Posts SET dislikes = dislikes + 1, points = points -1 WHERE id = %s'
    upd_id = execute_insert(upd_stmt, vote_data[1])
    answer = {"code": 0, "response": upd_id}
    return jsonify(answer)






