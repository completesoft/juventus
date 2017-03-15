import json
import os
import shutil
import time

try:
    from lib import *
except ImportError as e:
    shutil.unpack_archive(os.path.join(json.load(open("config.json", "r"))["tmp_dir"], "lib.zip"), os.getcwd(), format="zip")
    from lib import *
    logging.warn(e)


resp = request_comm(data={"action":"alive", "id": CONFIG_FILE["id"], "timestamp": int(time.time())})

if resp["status"] == "get_versions":
    resp = request_comm(data=CONFIG_FILE)

if resp["status"] == "update":
    for app in resp["software"]:
        loc_archive = request_comm(url=app["url"], file_path=CONFIG_FILE["tmp_dir"])
        if loc_archive == 1:
            continue
        if not hash_control(loc_archive, app["hash"]):
            continue
        mes = search_update(app)== 1
        if mes == 1:
            continue


if resp["status"] == "self" or resp["status"] == "self_lib":
    loc_archive = request_comm(url=resp["url"], file_path=CONFIG_FILE["tmp_dir"])
    if loc_archive == 1:
        logging.critical("Command \'update {}\' ABORT. Can\'t download {}".format(resp["status"], resp["url"]))
        sys.exit(1)
    if not hash_control(loc_archive, resp["software"][0]["hash"]):
        sys.exit(1)
    try:
        if resp["status"] == "self":
            shutil.move(sys.argv[0], CONFIG_FILE["tmp_dir"])
            shutil.unpack_archive(loc_archive, os.getcwd(), format="zip")
        if resp["status"] == "self_lib":
            shutil.move(os.path.join(os.path.split(sys.argv[0])[0], "lib.py"), CONFIG_FILE["tmp_dir"])
            shutil.unpack_archive(loc_archive, os.getcwd(), format="zip")
    except Exception as e:
        logging.critical("Unzip fail: "+e)
        sys.exit(1)


if resp["status"] == "execute":
    loc_archive = request_comm(url=resp["url"], file_path=CONFIG_FILE["tmp_dir"])
    if loc_archive == 1:
        logging.critical("Command \'{}\' ABORT. Can\'t download {}".format(resp["status"], resp["url"]))
        sys.exit(1)
    if not hash_control(loc_archive, resp["software"][0]["hash"]):
        sys.exit(1)
    shutil.unpack_archive(loc_archive, extract_dir=CONFIG_FILE["tmp_dir"], format="zip")
    loc_path = os.path.splitext(loc_archive)[0]+".py"
    if not os.system("python {}".format(loc_path)):
        sys.exit(0)