# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify
from db_app.executor import *
import urlparse
from db_app.post_app.post_app import posts_to_list, serialize_post
from db_app.thread_app.thread_app import serialize_thread,threads_to_list
from db_app.user_app.user_app import serialize_user_email, serialize_user, get_following,get_followers,get_subscriptions

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



@app.route('/create/', methods=['POST'])
def create():
    data = request.get_json()
    print(data)
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
    print('Forum/details')
    try:
        data.append(request.args.get('forum'))
        select_stmt = ('SELECT * FROM Forums WHERE slug = %s')
        print(data)
        forum = execute_select(select_stmt, data)
        if len(forum) == 0 :
            return jsonify({"code":0, "response": []})
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    except Exception:
        answer = {"code": 1, "response": "incorrect related"}
        return jsonify(answer)
    if request.args.get('related') == 'user':
        user_info = serialize_user_email(forum[0][3])
        print(forum[0])
        print(user_info)
        print(serialize_forum_user(forum[0], user_info))
        answer = {"code": 0, "response": serialize_forum_user(forum[0], user_info)}
        print(answer)
        return jsonify(answer)
    answer = {"code": 0, "response": serialize_forum(forum[0])}
    return jsonify(answer)


@app.route('/listPosts/', methods=['GET'])
def listPosts():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"][0])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Posts WHERE forum = %s')
    try:
        data.append(req["since"][0])
        select_stmt += ' AND date >= %s'
    except KeyError:
        pass
    try:
        select_stmt += ' ORDER BY date ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY date ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s'
    except KeyError:
        pass
    print('listsPostsss')
    print(select_stmt)
    print(data)
    posts = execute_select(select_stmt, data)
    if len(posts) == 0:
        return jsonify({"code": 0, "response": []})
    print(posts)
    try:
        list1 = request.args.getlist('related')
    except KeyError:
        list1 = []
        return jsonify({"code": 0, "response": posts_to_list(posts)})
    resp = []
    for post in posts:
        thread_info = post[2]
        forum_info = post[5]
        user_info = post[4]
        for related in list1:
            if related == 'thread':
                thread = execute_select('SELECT * FROM Threads WHERE id = %s', int(thread_info))
                thread_info = serialize_thread(thread[0], thread[0][4], thread[0][1])
            elif related == 'forum':
                forum = execute_select('SELECT * FROM Forums WHERE slug = %s', forum_info)
                forum_info = serialize_forum(forum[0])
            elif related == 'user':
                user_info = serialize_user_email(user_info)
        post = serialize_post(post,user_info,forum_info,thread_info)
        resp.append(post)
    if len(resp) > 0:
        answer = {"code": 0, "response": resp}
        return jsonify(answer)
    else:
        return jsonify({"code": 0, "response": posts_to_list(posts)})



@app.route('/listThreads/', methods=['GET'])
def listThreads():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"][0])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Threads WHERE forum = %s')
    try:
        data.append(req["since"][0])
        select_stmt += ' AND date >= %s'
    except KeyError:
        pass
    try:
        select_stmt += ' ORDER BY date ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY date ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s'
    except KeyError:
        pass
    threads = execute_select(select_stmt, data)
    try:
        list = request.args.getlist('related')
    except KeyError:
        return jsonify({"code": 0, "response": threads_to_list(threads)})
    resp = []
    if len(threads) == 0:
        print('IS EMPTY!!!!!!')
        return jsonify({"code": 0, "response": []})
    for thread in threads:
        forum_info = thread[1]
        user_info = thread[4]
        for related in list:
            if related == 'forum':
                forum = execute_select('SELECT * FROM Forums WHERE slug = %s', forum_info)
                forum_info = serialize_forum(forum[0])
            elif related == 'user':
                user_info = serialize_user_email(user_info)
        thread = serialize_thread(thread,user_info,forum_info)
        resp.append(thread)
    if len(resp) > 0:
        answer = {"code": 0, "response": resp}
        return jsonify(answer)
    else:
        return jsonify({"code": 0, "response": threads_to_list(threads)})


@app.route('/listUsers/', methods=['GET'])
def listUsers():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"][0])
    except KeyError:
        answer = {"code": 3, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Users WHERE email IN (SELECT DISTINCT user FROM Posts WHERE forum = %s)')
    try:
        data.append(int(req["since_id"][0]))
        select_stmt += ' AND id >= %s '
    except KeyError:
        pass
    try:
        select_stmt += ' ORDER BY name ' + req["order"][0]
    except KeyError:
        select_stmt += ' ORDER BY name ' + 'DESC'
        pass
    try:
        data.append(int(req["limit"][0]))
        select_stmt += ' LIMIT %s '
    except KeyError:
        pass
    users = execute_select(select_stmt, data)
    print(users)
    answer = {"code": 0, "response": users_to_list(users)}
    return jsonify(answer)


def users_to_list(users):
    resp = []
    for user in users:
        resp.append(serialize_user(user,get_subscriptions(user[4]), get_followers(user[4]), get_following(user[4])))
    print(resp)
    return resp

