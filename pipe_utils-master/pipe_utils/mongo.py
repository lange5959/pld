# -*- coding: utf-8 -*-

import json
import pymongo

host = '10.168.30.220'
port = 27017
user_name = 'admin'
user_pwd = '123456'


class SmMongo(object):
    def __init__(self, db_name, collection,
                 host=host, port=port,
                 user_name=user_name, user_pwd=user_pwd):
        """

        Args:
            db_name: 数据库名
            collection: 表名
        """
        super(SmMongo, self).__init__()

        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client.admin
        self.db.authenticate(user_name, user_pwd)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(collection)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('close db')
        self.client.close()

    def get_one(self, data):
        """

        Args:
            data (dict): filter data

        Returns (dict):

        """
        return self.collection.find_one(data)

    def get(self, data={}):
        """

        Args:
            data (dict):

        Returns (list):

        """
        result = []
        cursor = self.collection.find(data)
        for i in cursor:
            i["_id"] = str(i.get("_id"))
            # s = json.dumps(i, ensure_ascii=False)
            result.append(i)
        return result

    def insert(self, data):
        """

        Args:
            data (dict/list): [{},{}]/{}
        """
        if isinstance(data, dict):
            self.collection.insert_one(data)
        else:
            self.collection.insert(data)

    def delete(self, data):
        """

        Args:
            data (dict): {}
        """
        self.collection.delete_one(data)

    def update(self, data1, data2):
        data3 = {'$set': data2}
        self.collection.update_one(data1, data3)


if __name__ == '__main__':
    with SmMongo('ppline_test', 'students') as mo:
        data = mo.get_one({'id': '20170105'})
        print data
        # mo.delete(data)
