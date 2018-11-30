#/usr/bin/env python3

import hashlib
import http.server
import json
import os
import random
import shutil
import socketserver
import sys
import time

import requests
from flask import Flask, jsonify, render_template, request

import _thread

BASE = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)


appKey = '748dd544372b4354'
secretKey = 'jijsToUysU5C9YpZIx2mWbH7T8rdVO1O'

cache = {}
loaded = False
updated = False

def set_cache(k, v):
    global updated
    cache[k] = v
    updated = True

def load_cache():
    global cache, loaded
    with open(os.path.join(BASE, "words", "db.json")) as f:
        cache = json.loads(f.read())
    loaded = True

def dump_cache():
    global updated
    with open(os.path.join(BASE, "words", "db.json"), "w") as f:
        f.write(json.dumps(cache))
    updated = False

def cache_watchdog():
    # It may occurs race condition in multi-process situation.
    # But in production environment, we already cached all words.
    # It only runs in devloping stage.
    while True:
        time.sleep(1)
        if loaded and updated:
            try:
                dump_cache()
            except Exception as e:
                print(str(e), file=sys.stderr)

def first_true(l, default=None):
    for i in l:
        if i:
            return i
    return default

def query(word):
    word = word.strip()
    if word in cache:
        #print("query %s hit cache" % word)
        return cache[word]

    print("query %s thorugh Youdao API" % word)
    word = word.strip()
    salt = str(time.time())
    sign = appKey+word+salt+secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()

    params = {
        "appKey": appKey,
        "q": word,
        "from": "EN",
        "to": "zh-CHS",
        "salt": salt,
        "sign": sign
    }

    r = requests.get("https://openapi.youdao.com/api", params = params)
    if r.status_code != 200:
        raise Exception()
    t = json.loads(r.text)
    if int(t["errorCode"]) != 0:
        raise Exception(r.text)
    

    if not t["query"] or "basic" not in t:
        raise Exception("\"%s\" may be a wrong word" % word)
    word = t["query"]

    res = {
        "word": t["query"],
        "phonetic": first_true([t["basic"].get("us-phonetic"), t["basic"].get("uk-phonetic"), t["basic"].get("phonetic")], ""),
        "explains": t["basic"]["explains"],
        #"speech_url": first_true([t["basic"].get("us-speech"), t["basic"].get("uk-speech"), t["basic"].get("speakUrl")], ""),
        "speech_url": "https://dict.youdao.com/dictvoice?audio="+word+"&type=2"
    }

    set_cache(word, res)

    return res


def gen_wordlist(list_name):

    r = {
        "error": 0,
        "words": []
    }
    try:
        with open(os.path.join(BASE, "word_lists", list_name)) as f:
            for w in f.readlines():
                w = w.strip()
                if w:
                    r["words"].append(query(w))
    except Exception as e:
        r["error"] = 1
        r["error_msg"] = str(e)
    
    return r


def list_names():
    r = {
        "error": 0,
        "lists": []
    }
    try:
        for l in os.listdir(os.path.join(BASE, "word_lists")):
            if l.endswith(".txt"):
                r["lists"].append(l)
        r["lists"].sort()
    except Exception as e:
        r["error"] = 1
        r["error_msg"] = str(e)

    return r

def load(txt):
    p = os.path.join(BASE, "word_lists", txt)

    global word_list
    word_list = []
    with open(p, "r") as f:
        for w in f.readlines():
            if w:
                word_list.append(w.strip())
    random.shuffle(word_list)

load_cache()

def serve(path):
    os.chdir(path)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("127.0.0.1", 5000), Handler)
    print("serving at ", "http://127.0.0.1:5000")
    httpd.serve_forever()

def gen_public():
    os.system("rm -rf ./public")
    os.system("mkdir -p ./public ./public/word_lists")
    shutil.copytree("./static", "./public/static")
    shutil.copy("./templates/home.html", "./public/index.html")
    word_list_index = list_names()
    with open("./public/word_list_index.json", "w") as f:
        f.write(json.dumps(word_list_index))
    for name in word_list_index["lists"]:
        with open("./public/word_lists/%s" % name, "w") as f:
            l = gen_wordlist(name)
            if l["error"]:
                raise Exception("Occured error during generating %s: %s" % (name, l["error_msg"]))
            f.write(json.dumps(l))

if __name__ == '__main__':
    _thread.start_new_thread(cache_watchdog, ())
    gen_public()
    serve("./public")
