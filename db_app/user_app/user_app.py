from flask import jsonify, Blueprint
from flask import request
import db_app

from db_app.executor import *
import urlparse

app = Blueprint('user_app', __name__)


def serialize_user_email(email_user):
    select_stmt = ('SELECT * FROM Users WHERE email = %s')
    if len(email_user) != 1:
        user = execute_select(select_stmt, [email_user])
    else:
        user = execute_select(select_stmt, email_user)
    if len(user) == 0:
        return {}
    user = user[0]
    return serialize_user(user, get_subscriptions(email_user), get_followers(email_user), get_following(email_user))


def serialize_user_id(res):
    resp = {'about': res[1],
            'email': res[3],
            'id': res[5],
            'isAnonymous': bool(res[4]),
            'name': res[2],
            'username': res[0]
            }
    return resp


def lists_user_by_mails(mails):
    resp = []
    for mail in mails:
        user = execute_select('SELECT * FROM Users WHERE email = %s', mail)
        if len(user) == 0:
            return []
        resp.append(serialize_user(user[0], get_subscriptions(mail), get_followers(mail), get_following(mail)))
    return resp


def get_subscriptions(user):
    select_stmt = ('SELECT thread FROM Subscribe WHERE user = %s')
    if len(user) != 1:
        subscriptions = execute_select(select_stmt, [user])
    else:
        subscriptions = execute_select(select_stmt, user)
    if (len(subscriptions) == 0):
        return []
    res = []
    for subscription in subscriptions:
        res.append(subscription[0])
    return res


def get_followers(user):
    select_stmt = ('SELECT follower_mail FROM Followers WHERE following_mail = %s')
    if len(user) != 1:
        followers = execute_select(select_stmt, [user])
    else:
        followers = execute_select(select_stmt, user)
    if (len(followers) == 0):
        return []
    res = []
    for follower in followers:
        res.append(follower[0])
    return res


def get_following(user):
    select_stmt = ('SELECT following_mail FROM Followers WHERE follower_mail = %s')
    if len(user) != 1:
        followings = execute_select(select_stmt, [user])
    else:
        followings = execute_select(select_stmt, user)
    if (len(followings) == 0):
        return []
    res = []
    for following in followings:
        res.append(following[0])
    return res


def serialize_user(user, subscriptions, followers, following):
    resp = {'about': user[2],
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
    if (len(res) == 0):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE email = %s')
    usr = execute_select(select_stmt, [res[3]])
    if (len(usr) != 0):
        answer = {"code": 5, "response": "User already exists"}
        return jsonify(answer)
    insert_stmt = (
        'INSERT INTO Users (username, about, name, email, isAnonymous) '
        'VALUES (%s, %s, %s, %s, %s)'
    )
    user_id = execute_insert(insert_stmt, res)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE id = %s')
    resp = execute_select(select_stmt, [int(user_id)])
    res.append(resp[0][0])
    answer = jsonify({"code": 0, "response": serialize_user_id(res)})
    return answer


@app.route('/details/', methods=['GET'])
def details():
    qs = urlparse.urlparse(request.url).query
    mail = urlparse.parse_qs(qs)
    user_mail = mail["user"]
    return jsonify({"code": 0, "response": serialize_user_email(user_mail)})


def details_email(email):
    return jsonify({"code": 0, "response": serialize_user_email(email)})


def __parse_follow_request_data(json_data):
    res = []
    try:
        res.append((json_data["follower"]))
        res.append((json_data["followee"]))
    except KeyError:
        res = []
    return res


@app.route('/follow/', methods=['POST'])
def follow():
    user_data = request.json
    res = __parse_follow_request_data(user_data)
    if (len(res) == 0):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT follower_mail,following_mail FROM Followers WHERE follower_mail = %s && following_mail = %s')
    usr = execute_select(select_stmt, res)
    if (len(usr) != 0):
        answer = {"code": 5, "response": "Follower and following already exists"}
        return jsonify(answer)
    insert_stmt = (
        'INSERT INTO Followers (follower_mail, following_mail) '
        'VALUES (%s, %s)'
    )
    execute_insert(insert_stmt, res)
    return details_email(res[0])


@app.route('/listPosts/', methods=['GET'])
def listPosts():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["user"][0])
    except KeyError:
        answer = {"code": 3, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Posts WHERE user = %s')
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
    posts = execute_select(select_stmt, data)
    return jsonify({"code": 0, "response": db_app.post_app.post_app.posts_to_list(posts)})


@app.route('/updateProfile/', methods=['POST'])
def update():
    user_data = request.json
    res = []
    try:
        res.append(user_data["about"])
        res.append(user_data["name"])
        res.append(user_data["user"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Users SET about = %s, name = %s WHERE email = %s')
    execute_insert(update_stmt, res)
    select_stmt = ('SELECT * FROM Users WHERE email = %s')
    resp = execute_select(select_stmt, res[2])
    if len(resp) == 0:
        return jsonify({"code": 0, "response": []})
    sub = get_subscriptions(resp[0][4])
    following = get_following(resp[0][4])
    followers = get_followers(resp[0][4])
    answer = jsonify({"code": 0, "response": serialize_user(resp[0], sub, following, followers)})
    return answer


@app.route('/listFollowers/', methods=['GET'])
def listFollowers():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["user"][0])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = 'SELECT follower_mail FROM Followers WHERE following_mail = %s'
    try:
        data.append(int(req["since_id"][0]))
        select_stmt += ' AND id >= %s'
    except KeyError:
        pass
    try:
        select_stmt += ' ORDER BY following_mail ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY following_mail ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s'
    except KeyError:
        pass
    mails = execute_select(select_stmt, data)
    if len(mails) == 0:
        return jsonify({"code": 0, "response": []})
    all_users = lists_user_by_mails(mails[0])
    return jsonify({"code": 0, "response": all_users})


@app.route('/listFollowing/', methods=['GET'])
def listFollowing():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    count = 0
    try:
        data.append(req["user"][0])
        count += 1
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = 'SELECT following_mail FROM Followers WHERE follower_mail = %s'
    try:
        data.append(int(req["since_id"][0]))
        select_stmt += ' AND id >= %s'
        count += 1
    except KeyError:
        pass
    try:
        select_stmt += ' ORDER BY follower_mail ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY follower_mail ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s'
    except KeyError:
        pass
    mails = execute_select(select_stmt, data)
    if len(mails) == 0:
        return jsonify({"code": 0, "response": []})
    all_users = lists_user_by_mails(mails[0])
    return jsonify({"code": 0, "response": all_users})


@app.route('/unfollow/', methods=['POST'])
def unfollow():
    user_data = request.json
    data = []
    try:
        data.append(user_data["follower"])
        data.append(user_data["followee"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    delete_stmt = ('DELETE FROM Followers WHERE follower_mail = % s AND following_mail = % s')
    execute_insert(delete_stmt, data)
    return jsonify({"code": 0, "response": serialize_user_email(data[0])})
