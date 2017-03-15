import requests
import json
import os, sys
import shutil
import hashlib
import psutil
import logging

logging.basicConfig(format = '[%(asctime)-19s] # %(levelname)-8s # --%(message)s-- #%(filename)s[LINE:%(lineno)d]#', level = logging.DEBUG, filename='client_log.log',datefmt='%Y-%m-%d %H:%M:%S')
CONFIG_FILE = json.load(open("config.json", "r"))


def request_comm(url=CONFIG_FILE["url"], data=None, file_path=None):
    url = url
    if not file_path:
        headers = {"content-type": "application/json"}
        data = data
        try:
            r = requests.post(url, headers=headers, json=data)
        except requests.RequestException as e:
            logging.critical("{}".format(type(e).__name__))
            sys.exit(1)
        return r.json()
    else:
        local_archive_name = os.path.join(file_path, os.path.basename(url))
        try:
            r = requests.post(url)
            with open(local_archive_name, "wb") as code:
                code.write(r.content)
        except requests.RequestException as e:
            logging.critical("{}".format(type(e).__name__))
            return 1
        return local_archive_name


def search_update(ext_app_dict):
    local_app_dict = [app for app in CONFIG_FILE["software"] if app["name"] == ext_app_dict["name"]][0]
    zip_file = os.path.join(CONFIG_FILE["tmp_dir"], os.path.split(ext_app_dict["url"])[1])

    # Taskkill all processes from local_path dir
    process_id = [proc.pid for proc in psutil.process_iter()]
    for pid in process_id:
        p = psutil.Process(pid)
        try:
            path = p.exe()
        except:
            path = ""
        if path and ((local_app_dict["local_path"]+"\\") in (os.path.split(path)[0]+"\\")):
            os.system("taskkill /f /pid {}".format(pid))

    # Make backup.zip
    arch_path = os.path.join(CONFIG_FILE["backup_dir"], "{0}_{1}".format(local_app_dict["name"], local_app_dict["version"]))
    try:
        shutil.make_archive(arch_path, format='zip', root_dir=local_app_dict["local_path"])
    except Exception as e:
        logging.critical("Unzip fail:"+e)
        return 1


    # Unzip and update file(s)
    try:
        shutil.unpack_archive(zip_file, extract_dir=local_app_dict["local_path"], format="zip")
    except Exception as e:
        logging.critical("Copying files ABORT: "+e)
        return 1
    else:
        mes = config_update(ext_app_dict)

    return mes


def config_update(ext_app_dict):
    try:
        config = json.load(open("config.json", "r"))
        for app in config["software"]:
            if app["name"] == ext_app_dict["name"]:
                app["version"] = ext_app_dict["version"]
                break
        with open("config.json", "w") as file:
            json.dump(config, file, indent=4, sort_keys=True)
    except Exception as e:
        logging.error("Запись в config не сделана. Приложение {} обновлено до версии {}".format(ext_app_dict["name"], ext_app_dict["version"]))
    return 'Приложение: {} обновлено!'.format(ext_app_dict['name'])


def hash_control(file_path, hash_income):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chank in iter(lambda: f.read(2048), b""):
            hash_md5.update(chank)
    if hash_md5.hexdigest()== hash_income:
        logging.info("Hash compare - OK")
        return 0
    else:
        logging.critical("Hash control NOT pass")
        return 1





