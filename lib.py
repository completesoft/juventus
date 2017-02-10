import requests
import time
import json
import zipfile
import os
import shutil
import hashlib

softListPath = 'softList.txt'
softListLocal = json.load(open(softListPath, "r"))
work_station_id = 12345
url = 'http://localhost/python/phptest.php'
headers = {'content-type': 'application/json'}
localPathTemp = "D:/test"


def first_request():
    data = {"id": work_station_id, "timestamp": int(time.time()), "status": "ok"}
    r = requests.post(url, headers=headers, json=json.dumps(data))
    return r.json()


def download(urlDownLoad, localPath=localPathTemp):
    r = requests.post(urlDownLoad)
    with open(os.path.join(localPath, os.path.basename(urlDownLoad)), "wb") as code:
        code.write(r.content)
    code.close()


def archive_unzip_update(url_app):
    zip_obj = zipfile.ZipFile(os.path.join(localPathTemp+os.path.split(url_app)[1]))
    extract_list = zip_obj.namelist()
    zip_obj.extractall(localPathTemp)
    zip_obj.close()
    app_summary = get_app_on_name(url_app)
    for f in extract_list:
        if os.path.isfile(os.path.join(app_summary["cwd"], f)):
            name, extension = os.path.splitext(f)
            os.rename(os.path.join(app_summary["cwd"], f), os.path.join(app_summary["cwd"], (name+"_old"+extension)))
            shutil.move(os.path.join(localPathTemp, f), os.path.join(app_summary["cwd"], f))
        else:
            shutil.move(os.path.join(localPathTemp, f), os.path.join(app_summary["cwd"], f))




def ver_info():
    soft_info = {"id": work_station_id, "timestamp": int(time.time()), "status": "versions_info"}
    soft_info["software"] = json.load(open(softListPath, "r"))
    print(soft_info)
    r = requests.post(url, headers=headers, json=json.dumps(soft_info))
    return r.json()


def hash_control(urlDownload, hash_income):
    file_name= os.path.basename(urlDownload)
    hash_md5 = hashlib.md5()
    with open(localPathTemp+file_name, "rb") as f:
        for chank in iter(lambda: f.read(2048), b""):
            hash_md5.update(chank)
    return hash_md5.hexdigest if hash_md5.hexdigest()== hash_income else 0


def get_app_on_name(url_app):
    app_name = os.path.splitext(os.path.split(url_app)[1])[0]
    for app_summary in softListLocal:
        if app_name == app_summary["name"]:
            return app_summary
