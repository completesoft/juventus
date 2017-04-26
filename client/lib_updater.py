import requests
import json
import os, sys
import shutil
import hashlib
import psutil
import copy
import ctypes
import time
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
filehandler = logging.handlers.RotatingFileHandler('client_log.log', encoding='utf8', maxBytes=100000, backupCount=1)
formatter = logging.Formatter(fmt='[%(asctime)-19s] # %(levelname)-8s # %(message)-40s  #%(filename)s[LINE:%(lineno)d]#', datefmt='%Y-%m-%d %H:%M:%S')
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

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
            log.info("download - pass")
        return local_archive_name


def backup_update(app_dict):
    # path 1-loc app_conf, 2-path for zipper
    local_app_dict = [app for app in CONFIG_FILE["software"] if app["name"] == app_dict["name"]][0]
    zip_file = os.path.join(CONFIG_FILE["tmp_dir"], os.path.split(app_dict["url"])[1])

    # Create backup.zip
    arch_path = os.path.join(CONFIG_FILE["backup_dir"], "{0}_{1}".format(local_app_dict["name"], local_app_dict["version"]))
    file_name = shutil.make_archive(arch_path, format='zip', root_dir=local_app_dict["local_path"])

    if file_name:
        # Unzip and update file(s)
        shutil.unpack_archive(zip_file, extract_dir=local_app_dict["local_path"], format="zip")
        log.info("files update - pass")
        return local_app_dict["local_path"]
    else:
        raise Exception("backup - FAIL")


def config_update(ext_app_dict):
    # config = json.load(open("config.json", "r"))
    for app in CONFIG_FILE["software"]:
        if app["name"] == ext_app_dict["name"]:
            app["version"] = ext_app_dict["version"]
            break
    with open("config.json", "w") as file:
        json.dump(CONFIG_FILE, file, indent=4, sort_keys=True)
    log.info("app \"{}\" config - pass".format(app["name"]))
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
    local_app_dict = copy.deepcopy([app for app in CONFIG_FILE["software"] if app["name"] == app_dict["name"]][0])
    process_id = [proc for proc in psutil.process_iter()]
    for pid in process_id:
        try:
            path = pid.exe()
        except Exception:
            path = ""
        if path and ((local_app_dict["local_path"] + "\\") in (os.path.split(path)[0] + "\\")):
            if local_app_dict['dialog']==1:
                while psutil.pid_exists(pid.pid):
                    answ = ctypes.windll.user32.MessageBoxW(0, "Закройте приложение \"{}\" и нажмите ОК".format(pid.name()), "ОБНОВЛЕНИЕ ПРИЛОЖЕНИЯ", 4112)
            pid.kill()
    return 0


def check_pid():
    if not os.path.isfile(os.path.join(os.getcwd(), 'rub.pid')):
        return (0,0)
    with open('run.pid', 'r') as f_pid:
        pid = f_pid.read()
    if pid:
        try:
            f = psutil.Process(pid).exe()
        except Exception:
            #tuple describe [0]-pid in file, [1]-pid in process
            return(pid, 0)
        else:
            if f in os.getcwd():
                log.info("Updater on the work - second Updater stopped")
                sys.exit(1)
    else:
        #tuple describe: [0]-pid in file, [1]-pid in process
        return (pid, 0)


def set_pid(reset=False):
    if reset:
        pid=""
    else:
        pid = os.getpid()
    with open('run.pid', 'w') as f:
        f.write(str(pid))
    return pid



if __name__=='__main__':
    print(check_pid())





