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




