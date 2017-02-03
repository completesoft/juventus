import requests
import time
import json
import zipfile
import os
import shutil

soft_list = 'softList.txt'
id = 12345
url = 'http://localhost/python/phptest.php'
urlD = 'http://localhost/python/'
fileD = 'lib.zip'
localPathD = "D:/python/"


def zapros():
    data = {"id": id, "timestamp": int(time.time()), "status": "ok"}
    r = requests.post(url, data)
    respons = r.json()
    return respons


def download():
    fullpath=urlD+fileD
    r = requests.post(fullpath)
    with open(localPathD+fileD, "wb") as code:
        code.write(r.content)


def archive_rename():
    zipobj = zipfile.ZipFile(localPathD+fileD)
    zipobj.extractall(localPathD)
    # os.rename("lib.py", "lyb111.py")
    # shutil.move(localPathD+"lib.py", os.getcwd())








    # f=open(soft_list, 'w')
    # json.dump(r.json(),f)

