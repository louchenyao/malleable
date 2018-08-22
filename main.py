#/usr/bin/env python3

from flask import Flask, jsonify, request, render_template

import requests
import random
import hashlib
import time
import json
import os 
import sys
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

word_list = ["abandon", "good", "bad"]
word_p = 0

def first_true(l, default=None):
    for i in l:
        if i:
            return i
    return default

# def save_local(word, r):
#     with open("words/%s.json" % word, "w") as f:
#         f.write(json.dumps(r))

# def query_local(word):
#     with open("words/%s.json" % word) as f:
#         return json.loads(f.read())

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

@app.route('/rand')
def rand():
    # r = {
    #     "word": "good",
    #     "phonetic": "ɡʊd",
    #     "explains": ["adj. 好的；优良的；愉快的；虔诚的"],
    #     "speech_url": "http://openapi.youdao.com/ttsapi?q=good&langType=en&sign=337F61B28F0C70CD525038096944807F&salt=1534249304847&voice=6&format=mp3&appKey=748dd544372b4354",
    # }
    global word_p
    if word_p + 1 >= len(word_list):
        word_p = 0
    else:
        word_p += 1
    w = word_list[word_p]

    try:
        r = query(w)
        r["error"] = 0
    except Exception as e:
        r = {
            "word": w,
            "error": 1,
            "error_msg": str(e)
        }
    return jsonify(r)
    

@app.route('/word_list')
def download_word_list():
    list_name = request.args.get('name')

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
    return jsonify(r)

@app.route('/list_names')
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

    return jsonify(r)

@app.route('/')
def home():
    return render_template("home.html")

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

if __name__ == '__main__':
    _thread.start_new_thread(cache_watchdog, ())
    app.debug = True
    app.run()
