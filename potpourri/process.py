#! /usr/bin/env python3

from server import query
import json

def process(txt="word_list.txt"):
    with open(txt) as f:
        for l in f.readlines():
            l = l.strip()
            print("Processing", l)
            if l:
                try:
                    r = query(l)
                    with open("../words/%s.json" % l, "w") as ff:
                        ff.write(json.dumps(r))
                except Exception as e:
                    print(e)


process("word_list_15.txt")