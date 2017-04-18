import requests
import json
import os, sys
import shutil
import hashlib
import psutil
import copy
import ctypes
import logging, logging.handlers

log = logging.getLogger(__name__)

CONFIG_FILE = json.load(open("config.json", "r"))


def request_comm(url=CONFIG_FILE["url"], data=None, file_path=None):
    url = url
    if not file_path:
        headers = {"content-type": "application/json"}
        data = data
        r = requests.post(url, headers=headers, json=data)
        return r.json()
    else:
        local_archive_name = os.path.join(file_path, os.path.basename(url))
        r = requests.post(url)
        with open(local_archive_name, "wb") as code:
            code.write(r.content)
        return local_archive_name


def search_update(ext_app_dict):
    local_app_dict = [app for app in CONFIG_FILE["software"] if app["name"] == ext_app_dict["name"]][0]
    zip_file = os.path.join(CONFIG_FILE["tmp_dir"], os.path.split(ext_app_dict["url"])[1])

    # Taskkill all processes from local_path dir
    task_killer(local_app_dict)



    # Create backup.zip
    arch_path = os.path.join(CONFIG_FILE["backup_dir"], "{0}_{1}".format(local_app_dict["name"], local_app_dict["version"]))
    shutil.make_archive(arch_path, format='zip', root_dir=local_app_dict["local_path"])

    # Unzip and update file(s)
    shutil.unpack_archive(zip_file, extract_dir=local_app_dict["local_path"], format="zip")
    return local_app_dict["local_path"]


def config_update(ext_app_dict):
    config = json.load(open("config.json", "r"))
    for app in config["software"]:
        if app["name"] == ext_app_dict["name"]:
            app["version"] = ext_app_dict["version"]
            break
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4, sort_keys=True)
    return 0


def hash_control(file_path, hash_income):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chank in iter(lambda: f.read(2048), b""):
            hash_md5.update(chank)
    if hash_md5.hexdigest()== hash_income:
        log.info("Hash compare - OK")
        return 0
    else:
        raise Exception("Hash control NOT pass")


def task_killer(app_dict):
    local_app_dict = copy.deepcopy(app_dict)
    process_id = [proc for proc in psutil.process_iter()]
    for pid in process_id:
        try:
            path = pid.exe()
        except Exception:
            path = ""
        if path and ((local_app_dict["local_path"] + "\\") in (os.path.split(path)[0] + "\\")):
            ctypes.windll.user32.MessageBoxW(0, "Закройте приложение \"{}\" и нажмите ОК".format(local_app_dict["name"]), "ОБНОВЛЕНИЕ ПРИЛОЖЕНИЯ", 4112)
            pid.kill()
    return 0