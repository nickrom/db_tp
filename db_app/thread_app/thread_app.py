import datetime
from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *
from db_app.user_app.user_app import serialize_user_email
import db_app.forum_app.forum_app
from db_app.global_func import posts_to_list
import urlparse

app = Blueprint('thread_app', __name__)


def threads_to_list(posts):
    resp = []
    for post in posts:
        resp.append(serialize_thread(post, post[4], post[1]))
    print(resp)
    return resp


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
        #'points': thread[9]-thread[8],
        'slug': thread[6],
        'title': thread[1],
        'user': thread[3]
    }
    return resp


def serialize_thread1(thread, thread_id):
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
        'dislikes': thread[11],
        'forum': forum_info,
        'id': thread[0],
        'isClosed': bool(thread[3]),
        'isDeleted': bool(thread[8]),
        'likes': thread[10],
        'message': thread[6],
        'slug': thread[7],
        'title': thread[2],
        'posts': thread[9],
        'user': user_info,
        'points': thread[12]
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
    print('Thread/details')
    try:
        data.append(request.args.get('thread'))
        select_stmt = ('SELECT * FROM Threads WHERE id = %s')
        print(data)
        thread = execute_select(select_stmt, data)
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    except Exception:
        answer = {"code": 1, "response": "incorrect related"}
        return jsonify(answer)
    list = request.args.getlist('related')
    if len(thread) == 0:
        return jsonify({"code": 0, "response": []})
    user_info = thread[0][4]
    forum_info = thread[0][1]
    for related in list:
        if related == 'user':
            user_info = serialize_user_email(thread[0][4])
        elif related == 'forum':
            forum_info = serialize_forum1(thread[0][1])
        elif related == 'thread':
            print('Privet')
            return jsonify({"code":3, "response": "incorrect related"})
    print("Details")
    print(serialize_thread(thread[0], user_info, forum_info))
    answer = jsonify({"code": 0, "response": serialize_thread(thread[0], user_info, forum_info)})
    return answer


@app.route('/list/', methods=['GET'])
def list():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["user"][0])
        select_stmt = ('SELECT * FROM Threads WHERE user = %s')
    except KeyError:
        try:
            data.append(req["forum"][0])
            select_stmt = ('SELECT * FROM Threads WHERE forum = %s')
        except KeyError:
            answer = {"code": 3, "response": "incorrect request"}
            return jsonify(answer)
    try:
        data.append(req["since"][0])
        select_stmt += ' AND date > %s '
    except KeyError:
        pass
    try:
        select_stmt += ' ORDER BY date ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY date ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s '
    except KeyError:
        pass
    print('THREAD LIST')
    print(select_stmt)
    print(data)
    threads = execute_select(select_stmt, data)
    print(threads)
    answer = {"code": 0, "response": threads_to_list(threads)}
    return jsonify(answer)


@app.route('/listPosts/', methods=['GET'])
def listPosts():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["thread"][0]) #0
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Posts WHERE thread = %s')
    try:
        data.append(req["since"][0]) #1
        select_stmt += ' AND date > %s '
    except KeyError:
        pass
    try:
        sort = req["sort"][0]
    except KeyError:
        sort = 'flat'
    try:
        order = req["order"][0]
    except KeyError:
        order = 'desc'
        pass
    try:
        limit = req["limit"][0] #2???
        limit = int(limit)
    except KeyError:
        limit = None
        pass
    select_stmt += ' ORDER BY date '
    if sort == 'flat':
        select_stmt += order
        if limit:
            select_stmt += ' LIMIT %s'
            data.append(limit)
    print(select_stmt)
    print(data)
    posts = execute_select(select_stmt, data)
    if len(posts) == 0:
        return jsonify({"code": 0, "response": []})
    if sort in {'tree', 'parent_tree'}:
        cats = {}
        for x in posts:
            print(x)
            if x[6] is None:
                try:
                    cats['root'].append(x)
                except KeyError:
                    cats['root'] = [x]
            else:
                try:
                    cats[x[6]].append(x)
                except:
                    cats[x[6]] = [x]
        if sort == 'parent_tree':
            cats['root'] = cats['root'][:limit]
        if order == 'desc':
            cats['root'].reverse()
        result = []
        root_h = ['root']
        while cats[root_h[-1]]:
            curr_ell = cats[root_h[-1]][0]
            result.append(curr_ell)
            del cats[root_h[-1]][0]
            if curr_ell[0] in cats and cats[curr_ell[0]]:
                root_h.append(curr_ell[0])
            elif not cats[root_h[-1]]:
                while root_h and not cats[root_h[-1]]:
                    root_h = root_h[:-1]
                if not root_h:
                    break
            if sort == 'tree' and len(result) >= limit:
                break
        posts = result
    answer = {"code": 0, "response": posts_to_list(posts)}
    return jsonify(answer)


@app.route('/remove/', methods=['POST'])
def remove():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Threads SET isDeleted = 1, posts = 0 WHERE id = %s')
    execute_insert(upd_stmt, rem_data[0])
    upd_stmt = ('UPDATE Posts SET isDeleted = 1 WHERE thread = %s')
    execute_insert(upd_stmt, rem_data[0])
    answer = {"code": 0, "response": rem_data[0]}
    return jsonify(answer)


@app.route('/restore/', methods=['POST'])
def restore():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Posts SET isDeleted = 0 WHERE thread = %s')
    execute_insert(upd_stmt, rem_data[0])
    num = execute_select('SELECT * FROM Posts WHERE thread = %s', rem_data[0])
    upd_stmt = ('UPDATE Threads SET isDeleted = 0, posts = %s WHERE id = %s')
    ans = execute_insert(upd_stmt, [len(num), rem_data[0]])
    print('restore')
    print(rem_data[0])
    print(num)
    answer = {"code": 0, "response": rem_data[0]}
    return jsonify(answer)


@app.route('/close/', methods=['POST'])
def close():
    thread_data = request.json
    try:
        thread_id = thread_data["thread"]
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Threads SET isClosed = 1 WHERE id = %s')
    execute_insert(update_stmt, thread_id)
    answer = {"code": 0, "response": thread_id}
    return jsonify(answer)


@app.route('/update/', methods=['POST'])
def update():
    data = request.json
    up_data = []
    try:
        up_data.append(data["message"])
        up_data.append(data["slug"])
        up_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Threads SET message = %s, slug = %s WHERE id = %s')
    ins_id = execute_insert(update_stmt, up_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)


@app.route('/vote/', methods=['POST'])
def vote():
    data = request.json
    vote_data = []
    upd_stmt = ()
    try:
        vote_data.append(data["vote"])
        vote_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    if(vote_data[0] == 1):
        upd_stmt = ('UPDATE Threads SET likes = likes + 1, points = points + 1 WHERE id = %s')
    if(vote_data[0] == -1):
        upd_stmt = ('UPDATE Threads SET dislikes = dislikes + 1, points = points - 1 WHERE id = %s')
    upd_id = execute_insert(upd_stmt, vote_data[1])
    answer = {"code": 0, "response": upd_id}
    return jsonify(answer)


@app.route('/open/', methods=['POST'])
def open():
    thread_data = request.json
    try:
        thread_id = thread_data["thread"]
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Threads SET isClosed = 0 WHERE id = %s')
    execute_insert(update_stmt, thread_id)
    answer = {"code": 0, "response": thread_id}
    return jsonify(answer)


@app.route('/subscribe/', methods=['POST'])
def subscribe():
    data = request.json
    sub_data = []
    try:
        sub_data.append(data["user"])
        sub_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    print(sub_data)
    ins_stmt = 'INSERT INTO Subscribe (user, thread) VALUES (%s, %s)'
    ins_id = execute_insert(ins_stmt, sub_data)
    answer = {"code": 0, "response": {"thread": sub_data[1], "user": sub_data[0]}}
    return jsonify(answer)


@app.route('/unsubscribe/', methods=['POST'])
def unsubscribe():
    data = request.json
    sub_data = []
    try:
        sub_data.append(data["thread"])
        sub_data.append(data["user"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    ins_stmt = 'DELETE FROM Subscribe WHERE thread = %s AND user = %s'
    ins_id = execute_insert(ins_stmt, sub_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)

