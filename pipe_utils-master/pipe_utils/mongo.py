# -*- coding: utf-8 -*-
# Time    : 2021/8/4 13:59
# Author  : MengWei

import json
import pymongo

host = '0.0.8.0'
port = 27017
# user_name = 'root '
# user_pwd = 'txjcCTFVTshG9RA'
user_name = 'admin'
user_pwd = '000'


class LcaMongo(object):
    def __init__(self, db_name, collection,
                 host=host, port=port,
                 user_name=user_name, user_pwd=user_pwd):
        """

        Args:
            db_name: 数据库名
            collection: 表名
        """
        super(LcaMongo, self).__init__()

        self.client = pymongo.MongoClient(host=host, port=port,
                                          username=user_name,
                                          password=user_pwd)
        self.db = self.client.admin
        # self.db.authenticate(user_name, user_pwd)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(collection)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
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

    def add(self, data):
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


def fn():
    with LcaMongo('ppline_test', 'students') as mo:
        # data = mo.get_one({'id': '20170105'})
        mo.insert({'name': 'cat'})


def fn2():
    with LcaMongo('ppline_test', 'students') as mo:
        # data = mo.get_one({'id': '20170105'})
        result = mo.get_one({'name': 'cat'})
        if result:
            result['_id'] = str(result['_id'])

        print(result)
        return result
        # print(result)


if __name__ == '__main__':
    pass
    result = fn2()
    print(type(result))
    print(result)



    # with LcaMongo('ppline_test', 'students') as mo:
    # data = mo.get_one({'id': '20170105'})
    # mo.insert({'name': 'cat'})
    # print(data)
    # mo.delete(data)
