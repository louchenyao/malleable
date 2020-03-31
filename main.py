#/usr/bin/env python3

import hashlib
import json
import os
import random
import shutil
import sys
import time
import traceback
import requests
from tqdm import tqdm


BASE = os.path.dirname(os.path.realpath(__file__))

config = json.load(open(os.path.join(BASE, 'config.json')))
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
        f.write(json.dumps(cache, indent=4))
    updated = False

def first_true(l, default=None):
    for i in l:
        if i:
            return i
    return default

def query(word):
    word = word.strip()
    if word in cache:
        return cache[word]

    print(f"query {word} thorugh Youdao API")
    word = word.strip()
    salt = str(time.time())
    sign = config['appKey'] + word + salt + config['appSecret']
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
        "speech_url_youdao": first_true([t["basic"].get("us-speech"), t["basic"].get("uk-speech"), t["basic"].get("speakUrl")], ""),
        "speech_url": "https://dict.youdao.com/dictvoice?audio="+word+"&type=2"
    }

    set_cache(word, res)

    return res


def gen_wordlist(list_name):

    print('Processing {}'.format(list_name))
    r = {
        "error": 0,
        "words": []
    }
    try:
        with open(os.path.join(BASE, "word_lists", list_name)) as f:
            for w in tqdm(f.readlines()):
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

def gen_public(dir='public'):
    os.system(f'rm -rf ./{dir}')
    os.system(f'mkdir -p ./{dir} ./{dir}/word_lists')
    shutil.copytree(f'./static', f'./{dir}/static')
    shutil.copy(f'./templates/home.html', f'./{dir}/index.html')
    word_list_index = list_names()
    with open(f'./{dir}/word_list_index.json', "w") as f:
        f.write(json.dumps(word_list_index, indent=4))
    for name in word_list_index["lists"]:
        with open(f'./{dir}/word_lists/{name}.json', "w") as f:
            l = gen_wordlist(name)
            if l["error"]:
                raise Exception(f'Occured error during generating {name}: {l["error_msg"]}')
            f.write(json.dumps(l, indent=4))

if __name__ == '__main__':
    load_cache()
    try:
        gen_public('public')
    except:
        traceback.print_exc()
    dump_cache()

