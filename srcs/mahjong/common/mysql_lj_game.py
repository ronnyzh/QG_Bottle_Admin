#!/usr/bin/env python
#-*-coding:utf-8 -*-

"""
@Author: $Author$
@Date: $Date$
@version: $Revision$

Description:
    mysql模块函数
"""
import time,datetime
import traceback
import pymysql

# import logging
# import logging.handlers

# DB_CONFIG = {'host':'test2.qianguisy.com','user':'user','password':'Einiter','db':'lj_game'}
DB_CONFIG   = {'host':'127.0.0.1','user':'root','password':'x.091015%','db':'lj_game'}
conn_list = {}

class MysqlljgameInterface(object):

    @staticmethod
    def getConn():
        try:
            the_conn = pymysql.connect(host=DB_CONFIG['host'], user=DB_CONFIG['user'], passwd=DB_CONFIG['password'],port=DB_CONFIG.get('port', 3306), db=DB_CONFIG['db'], charset='utf8')
            the_conn.autocommit(1)
            return the_conn

        except Exception as e:
            traceback.print_exc()

    @classmethod
    def excute_sql(cls,conn,sql):
        cursor = conn.cursor()
        cursor.execute(sql)
        return cls.get_mysql_result(cursor)

    @classmethod
    def get_mysql_result(cls,cursor,size=10000):
        '''每次获取10000条记录
        '''
        while True:
            result = cursor.fetchmany(size)
            if not result:
                cursor.close()
                break
            for line in result:
                yield line

    @classmethod
    def select(cls,sql='',fetchmany=False):
        results = []
        try:
            if sql:
                the_conn = cls.getConn()
                if fetchmany:
                    results = cls.excute_sql(the_conn,sql)
                else:
                    cursor = the_conn.cursor()
                    cursor.execute(sql)
                    results = cursor.fetchall()
                    cursor.close()

                the_conn.close()

            return results

        except Exception as e:
            traceback.print_exc()

    @classmethod
    def insert(cls,table,sql='',**kwargs):
        if table and kwargs:
            try:
                if sql:
                    _sql = sql
                else:
                    _sql = 'INSERT INTO %s%s VALUES%s' % (
                        table,
                        str(tuple(kwargs.keys())).replace('\'', ''),
                        str(tuple(kwargs.values()))
                    )
                #print _sql
                the_conn = cls.getConn()
                cursor = the_conn.cursor()
                cursor.execute(_sql)
                # results = cursor.fetchall()
                cursor.close()
                the_conn.close()

            except Exception as e:
                traceback.print_exc()

# if __name__ == '__main__':
#     print 'start'
#     curTime = datetime.datetime.now()
#     strTime = curTime.strftime('%Y-%m-%d %H:%M:%S')
#     data = {
#         'user_id': 10086,
#         'name': 'test',
#         'createtime': strTime,
#         'pre_gold': 1,
#         'changed': 50,
#         'now_gold': int(1) + 50,
#         'action': 3  # 1:扣房费, 2:结算扣分, 3:每日领取
#     }
#
#     MysqlInterface.insert('log_gold',**data)
