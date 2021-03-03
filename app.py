import json
import os
import urllib.parse
from datetime import datetime
from pytz import timezone
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import make_response
from flask import redirect
from flask import request
import feedgenerator
from document import Document
from twitter import search_tweet
from keyword_list import get_keyword_list
from keyword_list import add_keyword
from keyword_list import modify_keyword
from keyword_list import delete_keyword

PASSWORD = os.environ["PASSWORD"]

app = Flask(__name__)

@app.route('/')
def index():
    keyword_list = get_keyword_list()
    return render_template('index.html', keyword_list=keyword_list)


@app.route('/admin')
def admin():
    keyword_list = get_keyword_list()
    message = request.args.get("message", default="", type=str) 
    return render_template('admin.html', keyword_list=keyword_list, message=message)

@app.route('/admin/add', methods=['POST'])
def keyword_add():
    if ("password" in request.form) == False  or ("keyword" in request.form) == False:
        return redirect("/admin") 
    if request.form["keyword"] == "":
        return redirect("/admin?message=" + urllib.parse.quote("キーワードが空白です。"))
    if request.form["password"] != PASSWORD:
        return redirect("/admin?message=" + urllib.parse.quote("パスワードが間違っています。"))
    
    keyword_list = get_keyword_list()
    if len(keyword_list) > 10:
        return redirect("/admin?message=" + urllib.parse.quote("登録可能なキーワードは１０個までです。"))
    
    add_keyword(request.form["keyword"])
    return redirect("/admin?message=" + urllib.parse.quote("キーワードが追加されました"))

@app.route('/admin/update/<id>', methods=['GET','POST'])
def keyword_modify(id):
    
    if request.method == 'GET':
        keyword_list = get_keyword_list()
        message = request.args.get("message", default="", type=str) 
        return render_template('modify.html', id=id, keyword=keyword_list[id], message=message)
    else:
        if ("password" in request.form) == False  or ("keyword" in request.form) == False:
            return redirect("/admin") 
        if request.form["keyword"] == "":
            return redirect("/admin/update/" + id + "?message=" + urllib.parse.quote("キーワードが空白です。"))
        if request.form["password"] != PASSWORD:
            return redirect("/admin/update/" + id + "?message=" + urllib.parse.quote("パスワードが間違っています。"))
        
        modify_keyword(id, request.form["keyword"])
        return redirect("/admin?message=" + urllib.parse.quote("キーワードが修正されました"))


@app.route('/admin/delete/<id>', methods=['GET','POST'])
def keyword_delete(id):
    if request.method == 'GET':
        keyword_list = get_keyword_list()
        message = request.args.get("message", default="", type=str) 
        return render_template('delete.html', id=id, keyword=keyword_list[id], message=message)
    else:
        if ("password" in request.form) == False:
            return redirect("/admin/delete/" + id)
        if request.form["password"] != PASSWORD:
            return redirect("/admin/delete/" + id + "?message=" + urllib.parse.quote("パスワードが間違っています。"))
    
        keyword_list = get_keyword_list()
        if id not in keyword_list:
            return redirect("/admin")
            
        delete_keyword(id)
        return redirect("/admin?message=" + urllib.parse.quote("キーワードを削除しました"))

@app.route('/trend/<id>')
def trend(id):
    keyword_list = get_keyword_list()
    if id not in keyword_list:
        return ""
    keyword = keyword_list[id]
    tweet_list = search_tweet(keyword)

    return render_template('trend.html', list=tweet_list, id=id)

@app.route('/feed/<id>')
def feed(id):
    keyword_list = get_keyword_list()
    if id not in keyword_list:
        return ""
    keyword = keyword_list[id]
    tweet_list = search_tweet(keyword)

    title = "「" + keyword + "」 - Twitter Hourly Trend Reporter"
    link = "https://twitter.com/"
    description = "「" + keyword + "」の最近のツィートです。"

    feed = feedgenerator.Rss201rev2Feed(title=title, link=link, description=description, language="ja")

    for tweet in tweet_list:
        title = "「" + keyword + "」の最新のツィートです。(" + tweet["created_at"] + ")"
        description = tweet["text"]
        link = "https://twitter.com/" + tweet["author_id"] + "/status/" + tweet["id"]
        
        jp = timezone('Asia/Tokyo')
        pubdate = datetime.strptime(tweet["created_at"], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=jp)
        pubdate.timetz
        feed.add_item(title=title, link=link, description=description, pubdate=pubdate)

    response = make_response(feed.writeString("utf-8"))
    response.headers["Content-Type"] = "application/xml"
    return response

port = int(os.environ["PORT"])

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=port,debug=False)