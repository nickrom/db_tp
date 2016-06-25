# -*- coding: utf-8 -*-
import MySQLdb


def __connect_to_db():
    return MySQLdb.connect(host='localhost', user='user', passwd='1234',
                           db='db_tp', charset='cp1251', use_unicode=True)


def execute_select(query, params):
    connection = __connect_to_db()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
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
