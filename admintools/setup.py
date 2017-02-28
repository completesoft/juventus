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


def download(source_path, local_path):
    r = request_setup(url=source_path)
    with open(os.path.join(local_path, os.path.basename(source_path)), "wb") as code:
        code.write(r)
    code.close()
    return os.path.join(local_path, os.path.basename(source_path))


def archive_unzip(src_file_path):
    zip_obj = zipfile.ZipFile(src_file_path)
    zip_obj.extractall(os.path.split(src_file_path)[0])
    zip_obj.close()


def get_pass():
    pw = getpass.getpass("Enter password: ")
    pw = hashlib.md5(str.encode(pw))
    return pw.hexdigest()


def request_setup(url=json.load(open("setup-config.json", "r"))["api"]["url"], data=None):
    url = url
    data = data
    headers = {"content-type": "application/json"}
    if data:
        r = requests.post(url, headers=headers, json=data)
        return r.json()
    else:
        r = requests.post(url)
        return r.content


def prepare_path():
    local_path = json.load(open("setup-config.json", "r"))["api"]["updater_dir"]
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        return local_path
    if os.path.exists(local_path) and not os.listdir(local_path):
        return local_path
    else:
        print("Директория установки не пустая, видимо клиент уже установлен")
        return 0


def register_f(client_name=""):
    # Check destination folder
    local_path = prepare_path()
    if not local_path:
        return 1

    if len(sys.argv) >= 3:
        client_name = sys.argv[2]
    if not client_name:
        print("Вы не указали имя клиента, можно использовать имя компьютера: {}.".format(platform.node()))
        ans = input("Использвать имя компьютера - \"y\", ввести своё - \"n\"")
        if ans in ("n", "N"):
            client_name = input("Введите имя клиента: ")
        else:
            client_name = platform.node()
    data = {"action": "register", "name": client_name}

    # Ask password
    pas = get_pass()
    data["key"] = pas

    resp = request_setup(data=data)

    if "status" in resp.keys() and resp["status"] == "registered":
        config = {"name": data["name"], "id": resp["id"], "key": resp["key"]}

        resp_1 = list_f(prnt=False)

        soft_info = [app for app in resp_1["software"] if app["name"] == "updater"][0]

        # local_path = prepare_path()
        updater_source_zip = download(soft_info["url"], local_path)
        archive_unzip(updater_source_zip)
        os.remove(updater_source_zip)

        # Make "tmp" and "backup" dir
        os.makedirs(os.path.join(local_path, "tmp"))
        os.makedirs(os.path.join(local_path, "backup"))

        # Add info to config.json
        config.update({"tmp_dir": "tmp",
                       "backup_dir": "backup",
                       "software": [
                      {
                       "name": soft_info["name"],
                       "version": soft_info["version"],
                       "local_path": local_path,
                       "dialog": 0,
                       "state": "normal"
                      }
            ]
        })

        json.dump(config, open(os.path.join(local_path, "config.json"), "w"), indent=4, sort_keys=True)
        print("Клиент УСПЕШНО установлен в каталог " + json.load(open("setup-config.json", "r"))["api"]["updater_dir"])

    else:
        print(resp)


def add_f(app_name=None, path=None):
    if len(sys.argv) >= 4:
        app_name = sys.argv[2]
        path = sys.argv[3]

    if not app_name or not path:
        print("Не хватает параметров")
        return 1

    if not os.access(os.path.join(json.load(open("setup-config.json", "r"))["api"]["updater_dir"], "config.json"), os.F_OK):
        print("Файл конфигурации клиента не найден")
        return 1

    conf_path = os.path.join(json.load(open("setup-config.json", "r"))["api"]["updater_dir"], "config.json")
    loc_conf_file = json.load(open(conf_path, "r"))
    loc_conf_file_soft = loc_conf_file["software"]

    loc_name_flag = False

    for w in loc_conf_file_soft:
        if w["name"] == app_name:
            loc_name_flag = True
            break

    if loc_name_flag:
        print("П/о с названием \"{}\" уже зарегестрировано в конфигурации".format(app_name))
        return 1

    conf_file = list_f(prnt=False)
    conf_file_soft = conf_file["software"]

    name_flag = False
    i = 0
    for w in conf_file_soft:
        if w["name"] == app_name:
            name_flag = True
            break
        i += 1

    if not name_flag:
        print("П/о с названием \"{}\" отсутствует в БД".format(app_name))
        return 1

    app_dict = {
        "name": app_name,
        "version": None,
        "local_path": path,
        "dialog": 0,
        "state": "update"
    }

    loc_conf_file["software"].append(app_dict)
    json.dump(loc_conf_file, open(conf_path, "w"), indent=4, sort_keys=True)
    print("П/о \"{}\" добавлено в конфигурацию".format(app_name))
    return 0


def del_f(app_name=None):
    if len(sys.argv) >= 3:
        app_name = sys.argv[2]

    conf_path = os.path.join(json.load(open("setup-config.json", "r"))["api"]["updater_dir"], "config.json")
    conf_file = json.load(open(conf_path, "r"))
    conf_file_soft = json.load(open(conf_path, "r"))["software"]

    name_flag = True
    i = 0
    for w in conf_file_soft:
        if w["name"] == app_name:
            name_flag = False
            break
        i += 1
    if name_flag:
        print("П/о с названием \"{}\" отсутствует в конфигурации".format(app_name))
        return 1

    conf_file["software"].pop(i)
    json.dump(conf_file, open(conf_path, "w"), indent=4, sort_keys=True)
    print("П/о с названием \"{}\" успешно удалено из конфигурации клиента".format(app_name))
    return 0


def list_f(prnt=True):
    prnt = prnt
    data = {"action": "get_list"}
    r = request_setup(data=data)
    if prnt:
        print(json.dumps(r, sort_keys=True, indent=4))
    return r


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in ("register", "add", "del", "list"):
        if sys.argv[1] == "register":
            register_f()
        if sys.argv[1] == "add":
            add_f()
        if sys.argv[1] == "del":
            del_f()
        if sys.argv[1] == "list":
            list_f()
    else:
        print(__doc__)
