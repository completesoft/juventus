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
import os
import platform

config_file = "setup-config.json"


def download(urlDownLoad, localPath = "D:/test"):
    r = requests.post(urlDownLoad)
    with open(os.path.join(localPath, os.path.basename(urlDownLoad)), "wb") as code:
        code.write(r.content)
    code.close()


def request_setup (key_md5, data):
    headers = {"content-type": "application/json"}
    data = data
    data["key"] = key_md5
    url = json.load(open(config_file, "r"))["api"]["url"]
    r = requests.post(url, headers=headers, json=data)
    if r.json()["status"] == "registered":
        list = {"action": "get_list"}
        r = requests.post(url, headers=headers, json=list)
        url_d = [app["url"] for app in r.json()["software"] if app["name"] == "updater"]
        download(url_d)
    else:
        ...
    return r.json()

def command(args):
    arg_l=args
    if arg_l[1] == "register":
        if len(arg_l) == 2:
            print("Вы не указали имя клиента, можно использовать имя компьютера: {}.".format(platform.node()))
            ans = input("Использвать имя компьютера - \"y\", ввести своё - \"n\"")
            ans = input("Введите имя клиента: ") if (ans.lower()!="y" or ans.lower()!="yes") else ans=""
            data = {"action": arg_l[1], "name": ans if ans else platform.node()}
        else:
            data = {"action": arg_l[1], "name": arg_l[2]}
    return data

    if args[1] == "add":
        ...
    if args[1] == "del":
        ...






command_list = {"register": 3, "add": 4, "del": 3, "list": 2}

if len(sys.argv) > 1 and sys.argv[1] in command_list and len(sys.argv)==command_list[sys.argv[2]]:
    pw = getpass.getpass("Enter password: ")
    pw = hashlib.md5(str.encode(pw))
    data = {"action": sys.argv[1], "name": sys.argv[2], "key":pw.hexdigest()}
    r = requests.post(url, headers=headers, json=data)
    print(r.json(),sep=",", end="\n")




else:
    print(__doc__)



