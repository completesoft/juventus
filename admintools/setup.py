"""
 _____               _     _       _____     ___ _
|     |___ _____ ___| |___| |_ ___|   __|___|  _| |_
|   --| . |     | . | | -_|  _| -_|__   | . |  _|  _|
|_____|___|_|_|_|  _|_|___|_| |___|_____|___|_| |_|
                |_|

          ***Скрипт установки клиента***

setup.py [команда [параметр]]

    Команда регистрации клиента:
        register имя_клиента

    Параметр:
        имя клиента
"""

import getpass
import json
import sys
import requests
import hashlib

headers = {"content-type": "application/json"}
url = json.load(open("setup-config.json", "r"))["api"]["url"]
command_list = ["register"]

if len(sys.argv) == 3 and sys.argv[1] in command_list:
    pw = getpass.getpass("Enter password: ")
    pw = hashlib.md5(str.encode(pw))
    data = {"action": sys.argv[1], "name": sys.argv[2], "key":pw.hexdigest()}
    r = requests.post(url, headers=headers, json=data)
    print(r.json(),sep=",", end="\n")
else:
    print(__doc__)



