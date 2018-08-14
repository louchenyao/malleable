#/usr/bin/env python3

from flask import Flask, jsonify, request, render_template

import requests
import random
import hashlib
import time
import json

app = Flask(__name__)


appKey = '748dd544372b4354'
secretKey = 'jijsToUysU5C9YpZIx2mWbH7T8rdVO1O'

cache = {}
word_list = ["abandon"]
word_p = 0

def first_true(l, default=None):
    for i in l:
        if i:
            return i
    return default

def query(word):
    if word in cache:
        return cache[word]

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
    
    res = {
        "word": t["query"],
        "phonetic": first_true([t["basic"].get("us-phonetic"), t["basic"].get("uk-phonetic"), t["basic"].get("phonetic")], ""),
        "explains": t["basic"]["explains"],
        "speech_url": first_true([t["basic"].get("us-speech"), t["basic"].get("uk-speech"), t["basic"].get("speakUrl")], ""),
    }

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

@app.route('/')
def home():
    return render_template("home.html")

def load():
    global word_list
    word_list = []
    with open("word_list.txt", "r") as f:
        for w in f.readlines():
            if w:
                word_list.append(w.strip())
    random.shuffle(word_list)


if __name__ == '__main__':
    load()
    app.debug = True
    app.run()
