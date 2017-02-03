import requests
import json, os, sys
import time, datetime
import lib

# url = 'http://localhost/python/phptest.php'
# headers = {'content-type': 'application/json'}


print(lib.zapros())
if lib.zapros()["action"]=="update":
    lib.download()
    # lib.archive_rename()