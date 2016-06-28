# -*- coding: utf-8 -*-
import MySQLdb
from collections import Iterable


def __connect_to_db():
    return MySQLdb.connect(host='localhost', user='root', passwd='23Nikita',
                           db='db_tp', charset='cp1251', use_unicode=True)


def execute_select(query, params):
    connection = __connect_to_db()
    cursor = connection.cursor()
    try:
        if isinstance(params, str):
            par = []
            par.append(params)
            params=par
        else:
            pass
        print('WORK EXECUTE: ')
        print(query)
        print(params)
        print('___________')
        cursor.execute(query, params)
        result = cursor.fetchall()
    except (Exception, MySQLdb.Error):
        print("Error select into database")
        raise
    finally:
        cursor.close()
        connection.close()
    return result


def execute_select1(query):
    connection = __connect_to_db()
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except (Exception, MySQLdb.Error):
        print("Error select into database")
        raise
    finally:
        cursor.close()
        connection.close()
    return result


def execute_insert(query, params):
    connection = __connect_to_db()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        entity_id = cursor.lastrowid
        connection.commit()
    except(Exception, MySQLdb.Error):
        print("Error insert into database")
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    return entity_id
