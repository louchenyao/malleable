#/usr/bin/env python3

import requests
import random
import hashlib
import time


appKey = '748dd544372b4354'
secretKey = 'jijsToUysU5C9YpZIx2mWbH7T8rdVO1O'

 
myurl = '/api'
q = 'abandon'
fromLang = 'EN'
toLang = 'zh-CHS'

salt = str(time.time())
sign = appKey+q+salt+secretKey
sign = hashlib.md5(sign.encode()).hexdigest()

params = {
    "appKey": appKey,
    "q": q,
    "from": fromLang,
    "to": toLang,
    "salt": salt,
    "sign": sign
}

r = requests.get("https://openapi.youdao.com/api", params = params)

print(r.text)
