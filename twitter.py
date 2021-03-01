import sys
import os
import json
import time
from requests_oauthlib import OAuth1Session
from document import Document

TWITTER_API = os.environ["TWITTER_API"]
TWITTER_API_CONSUMER_TOKEN = os.environ["TWITTER_API_CONSUMER_TOKEN"]
TWITTER_API_CONSUMER_SECRET_TOKEN = os.environ["TWITTER_API_CONSUMER_SECRET_TOKEN"]
TWITTER_API_AUTH_TOKEN = os.environ["TWITTER_API_AUTH_TOKEN"]
TWITTER_API_AUTH_SECRET_TOKEN = os.environ["TWITTER_API_AUTH_SECRET_TOKEN"]

def search_tweet(query):
    instance = Document.getInstance()
    object = instance.getValue(query)

    if object == "" or int(time.time()) - object["timestamp"] > 60 * 60:
        url = TWITTER_API + query + "&tweet.fields=author_id,id,text"
        client = OAuth1Session(TWITTER_API_CONSUMER_TOKEN, TWITTER_API_CONSUMER_SECRET_TOKEN, TWITTER_API_AUTH_TOKEN, TWITTER_API_AUTH_SECRET_TOKEN)
        response = client.get(url)
        json_response = json.loads(response.text)
        list = []
        if "data" in json_response:
            list = json_response["data"]
            instance.setValue(query, {"timestamp": int(time.time()), "list": list})
        return list
    else:
        return object["list"]
