#! /usr/bin/env python3

import os
import json

def query_local(word):
    with open("../words/%s.json" % word) as f:
        return json.loads(f.read())

def main():
    cache = {}
    with open("../words/db.json") as f:
        cache = json.loads(f.read())

    words = os.listdir("../words")
    for w in words:
        if w.endswith("json") and w != "db.json":
            word = w.split(".")[0]
            try:
                r = query_local(word)
            except Exception as e:
                print(e)
            assert("phonetic" in r)
            cache[word] = r
    with open("../words/db.json", "w") as f:
        f.write(json.dumps(cache))

    with open("../words/db.json") as f:
        cache = json.loads(f.read())
        print("%d words in db.json" % len(cache))

if __name__ == '__main__':
    main()