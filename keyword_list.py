import os
import uuid
import time
from cloudant.client import Cloudant
from document import Document

DB_ACCOUNT_NAME = None
DB_NAME = os.environ["DB_NAME"]
DB_API_KEY = os.environ["DB_API_KEY"]
DB_URL = os.environ["DB_URL"]

def get_keyword_list():
    instance = Document.getInstance()
    object = instance.getValue("keyword_list")
    if object == "" or int(time.time()) - object["timestamp"] > 24 * 60 * 60:
        client = Cloudant.iam(DB_ACCOUNT_NAME, DB_API_KEY, url=DB_URL, connect=True)
        database = client[DB_NAME]
        document = database["tweet_keyword_list"]
        list = document["list"]
        client.disconnect()
        instance.setValue("keyword_list", {"timestamp": int(time.time()), "list": list})
        return list
    else:
        return object["list"]

def add_keyword(keyword):
    client = Cloudant.iam(DB_ACCOUNT_NAME, DB_API_KEY, url=DB_URL, connect=True)
    database = client[DB_NAME]
    document = database["tweet_keyword_list"]
    list = document["list"]
    list[str(uuid.uuid1())] = keyword;
    document["list"] = list;
    document.save()
    instance = Document.getInstance()
    instance.setValue("keyword_list", {"timestamp": int(time.time()), "list": list})
    client.disconnect()

def delete_keyword(id):
    client = Cloudant.iam(DB_ACCOUNT_NAME, DB_API_KEY, url=DB_URL, connect=True)
    database = client[DB_NAME]
    document = database["tweet_keyword_list"]
    list = document["list"]
    list.pop(id)
    document["list"] = list;
    document.save()
    instance = Document.getInstance()
    instance.setValue("keyword_list", {"timestamp": int(time.time()), "list": list})
    client.disconnect()