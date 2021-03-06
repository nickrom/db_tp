# -*- coding: utf-8 -*-
import MySQLdb
from collections import Iterable


def __connect_to_db():
    return MySQLdb.connect(host='localhost', user='root', passwd='23Nikita',
                           db='db_tp', charset='cp1251', use_unicode=True)
connection = __connect_to_db()


def execute_select(query, params):

    cursor = connection.cursor()
    try:
        if not isinstance(params, tuple) and not isinstance(params, list):
            par = []
            par.append(params)
            params=par
        else:
            pass
        cursor.execute(query, params)
        result = cursor.fetchall()
    except (Exception, MySQLdb.Error):
        print("Error select into database")
        raise
    finally:
        cursor.close()
        #connection.close()
    return result


def execute_insert(query, params):
    #connection = __connect_to_db()
    cursor = connection.cursor()
    try:
        if not isinstance(params, tuple) and not isinstance(params, list):
            par = []
            par.append(params)
            params=par
        else:
            pass
        cursor.execute(query, params)
        entity_id = cursor.lastrowid
        connection.commit()
    except(Exception, MySQLdb.Error):
        print("Error insert into database")
        connection.rollback()
        raise
    finally:
        cursor.close()
        #connection.close()
    return entity_id
