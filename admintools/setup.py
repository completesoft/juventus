
"""Первичная регистрация имени рабочего места
******************************************
  **Скрипт установки клиента setup.py**

    setup.py [команда [параметр]]

            Команда регистрации клиента:
                register имя_клиента

            Параметр:
                имя клиента
"""

import sys
import requests


url = "http://hive.product.in.ua:8885/api"
headers = {"content-type": "application/json"}

command_list = ["register"]


if len(sys.argv) == 3 and sys.argv[1] in command_list:
    data = {"action": sys.argv[1], "name": sys.argv[2]}
    r = requests.post(url, headers=headers, json=data)
    print(r.json(),sep=",", end="\n")
else:
    print(__doc__)
input("Для завершения нажмите ENTER")
sys.exit()


