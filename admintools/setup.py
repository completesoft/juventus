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
import zipfile
import getpass
import json
import sys
import requests
import hashlib
import os
import platform

config_file = "setup-config.json"
localPath = json.load(open(config_file, "r"))["api"]["updater_dir"]

def archive_unzip(app_dir, app_file):
    zip_obj = zipfile.ZipFile(os.path.join(app_dir, app_file))
    extract_list = zip_obj.namelist()
    zip_obj.extractall(localPath)
    zip_obj.close()
    return extract_list

def download(urlDownLoad, local_Path = localPath):
    path_d = local_Path
    r = requests.post(urlDownLoad)
    with open(os.path.join(path_d, os.path.basename(urlDownLoad)), "wb") as code:
        code.write(r.content)
    code.close()
    return path_d, os.path.basename(urlDownLoad)

def request_setup (data):
    headers = {"content-type": "application/json"}
    data_first = data
    url = json.load(open(config_file, "r"))["api"]["url"]
    r = requests.post(url, headers=headers, json=data_first)
    if r.json()["status"] == "registered":
        conf_f = json.load(open(config_file, "r"))
        conf_f["id"] = r.json()["id"]
        conf_f["key"] = r.json()["key"]
        conf_f["name"] = data["name"]
        json.dump(conf_f,open(config_file, "w"))
        data_second = {"action": "get_list"}
        r = requests.post(url, headers=headers, json=data_second)
        soft_info_tmp = [app for app in r.json()["software"] if app["name"] == "updater"]
        soft_info = soft_info_tmp[0]
        path_d = download(soft_info["url"])
        extract_list = archive_unzip(path_d[0], path_d[1])
        del soft_info["description"]
        del soft_info["url"]
        soft_info["local_path"] = localPath
        soft_info["dialog"] = 0
        soft_info["state"] = "normal"
        conf_f = json.load(open(config_file, "r"))
        config_client = {
                        "id": conf_f["id"],
                        "name": conf_f["name"],
                        "key": conf_f["key"],
                        "tmp_dir": "tmp",
                        "backup_dir": "backup",
                        "software": soft_info
                        }
        json.dump(config_client, open(os.path.join(localPath, "config.json"), "w"))
        print("Клиент УСПЕШНО установлеН")
    else:
        return r.json()

def command(args):
    arg_l=args
    if arg_l[1] == "register":
        if len(arg_l) == 2:
            print("Вы не указали имя клиента, можно использовать имя компьютера: {}.".format(platform.node()))
            ans = input("Использвать имя компьютера - \"y\", ввести своё - \"n\"")
            if (ans.lower() != "y" or ans.lower() != "yes"):
                ans = input("Введите имя клиента: ")
            else:
                ans=""
            data = {"action": arg_l[1], "name": ans if ans else platform.node()}
        else:
            data = {"action": arg_l[1], "name": arg_l[2]}
        return data

    elif arg_l[1] == "add":
        ...

    elif args[1] == "del":
        ...

    elif args[1] == "list":
        ...

    else:
        print(__doc__)



# MAIN part

data = command(sys.argv)
pw = getpass.getpass("Enter password: ")
pw = hashlib.md5(str.encode(pw))
data["key"] = pw.hexdigest()
request_setup(data)

