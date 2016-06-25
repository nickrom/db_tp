from flask import jsonify, Blueprint
from db_app.executor import *

app = Blueprint('common_app', __name__)


@app.route('/status/', methods=['GET'])
def status():
    resp = []
    tables = ['Users', 'Threads', 'Forums', 'Posts']

    for table in tables:
        count = execute_select('SELECT COUNT(*) FROM ' + table,())
        resp.append(count[0][0])

    json = {
        'user': resp[0],
        'thread': resp[1],
        'forum': resp[2],
        'post': resp[3]
    }
    return jsonify({"code": 0, "response": json})


@app.route('/clear/', methods=['POST'])
def clear():
    execute_insert('SET FOREIGN_KEY_CHECKS=0', ())
    tables = ['Users', 'Threads', 'Forums', 'Posts', 'Followers', 'Subscribe']
    for table in tables:
        execute_insert('TRUNCATE TABLE ' + table, ())
    execute_insert('SET FOREIGN_KEY_CHECKS=1', ())
    return jsonify({"code": 0, "response": "OK"})
