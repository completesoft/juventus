import json
import os, sys
import shutil
import logging.handlers
import ctypes
import time
import traceback
import requests
from lib_updater import *

MES_UPDATE_SUCCESS = "Приложение \"{}\" обновлено.\r\n   Нажмите ОК"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
filehandler = logging.handlers.RotatingFileHandler('client_log.log', encoding='utf8', maxBytes=100000, backupCount=1)
formatter = logging.Formatter(fmt='[%(asctime)-19s] # %(levelname)-8s # %(message)-40s  #%(filename)s[LINE:%(lineno)d]#', datefmt='%Y-%m-%d %H:%M:%S')
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

check_pid()
set_pid(reset=False)
try:
    resp = request_comm(data={"action":"alive", "id": CONFIG_FILE["id"], "timestamp": int(time.time())})
except Exception as e:
    log.critical(e)
    sys.exit(1)

while resp["status"] != "none":

    if resp["status"] == "get_versions":
        data = {"action": "soft_versions", "id": CONFIG_FILE["id"], "timestamp": int(time.time()), "software": CONFIG_FILE["software"]}
        resp = request_comm(data=data)

    if resp["status"] == "update":
        # dict for recording update process
        summary = dict.fromkeys([k["name"] for k in resp["software"]])

        for app in resp["software"]:
            try:
                loc_archive = request_comm(url=app["url"], file_path=CONFIG_FILE["tmp_dir"])
                #hash_control(loc_archive, app["hash"])
                task_killer(app)
                backup_update(app)
                config_update(app)
            except Exception :
                log.critical(sys.exc_info()[0:2])
                log.critical(traceback.format_exc())
                log.critical("\"{}\" => Crash update".format(app['name']))
                summary[app['name']]="Crash update"
                continue
            else:
                ctypes.windll.user32.MessageBoxW(0, MES_UPDATE_SUCCESS.format(app["description"]), "ОБНОВЛЕНИЕ ПРИЛОЖЕНИЯ", 4160)
                log.debug("\"{}\" => Successful update".format(app['name']))
                summary[app['name']]="Successful update"
        log.info("*Summed updating:*")
        for k in summary:
            log.info("***{} => {}".format(k, summary[k]))
        set_pid(reset=True)
        resp = request_comm(data={"action": "update_complete", "id": CONFIG_FILE["id"], "timestamp": int(time.time())})
