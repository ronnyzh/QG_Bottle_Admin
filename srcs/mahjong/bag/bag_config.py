import redis
import pymysql

bag_redis = redis.Redis(host='172.18.176.177',password="168joyvick",db="2",port=6381)
# bag_redis = redis.Redis(host='120.79.141.135',password="Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm",db="2")

class Mysql_instance(object):
    def __init__(self,host="172.18.176.196",port=3306,user="root",passwd="168mysql",db="bag_data"):
        self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()





