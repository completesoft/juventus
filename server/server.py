from flask import Flask
from flask import jsonify
from flask import request
import time
import MySQLdb
import json
import hashlib

DEBUG = True
# DEBUG = False

CONFIG_JSON = "server-config.json"
config = json.load(open(CONFIG_JSON, "r"))

app = Flask(__name__)


@app.route("/")
def hello():
    return "I'm ok"


@app.route("/api", methods=['POST'])
def api():
    # admintools`s registration block
    resp = {"status": "none"}
    content = request.get_json(silent=True)
    if content:
        if "action" in content:
            if content["action"] == "register":
                if "name" and "key" in content:
                    new_id = register_drone(content["name"])
                    if new_id:
                        hashkey = hashlib.md5(str.encode(str(new_id))).hexdigest()
                        resp = {"status": "registered", "id": new_id, "key": hashkey}
                    else:
                        resp = {"error": "name already registered"}
                else:
                    resp = {"error": "I want more options"}

# client`s conversation block
            if content["action"] == "alive":
                if "id" and "timestamp" in content:
                    drone_event(content["id"], content["timestamp"], 1)
                    resp = {"status": "get_versions"}
                    return jsonify(resp)
                else:
                    resp = {"error": "I want more options"}

            if content["action"] == "soft_versions":
                if "id" and "software" in content:
                    # # for soft_item in content["software"]:
                    # resp = {"status": "update", "software": [{"name": content["software"][1]["name"],
                    #         "version": 2018030355, "url": "http://update.product.in.ua/new/test/test_update.zip", "hash": "f5b805c107ddf2ceabc836ea9105374d"}]}
                    print("IN SOFT VERSION")
                    resp = soft_list(content)
                else:
                    resp = {"error": "I want more options"}

            if content["action"] == "get_list":
                list = get_list_software()
                resp = {"software": list}

            if content["action"] == "update_complete":
                resp = {"status": "none"}
    return jsonify(resp)


def time_stamp():
    return time.time()


def drone_event(drone_id, drone_timestamp, event_id):
    db = MySQLdb.connect(host="localhost", user="root", passwd=config["database"]["password"], db="hive")
    cursor = db.cursor()
    query = ('''INSERT INTO events (drone_id, drone_timestamp, event_id) VALUES ({0},FROM_UNIXTIME({1}),{2}) '''
                    ''' ON DUPLICATE KEY UPDATE drone_timestamp=FROM_UNIXTIME({1})'''
                   .format(drone_id, drone_timestamp, event_id))
    print(query)
    cursor.execute(query)
    db.commit()
    return 1


def get_list_software():
    db = MySQLdb.connect(host=config["database"]["host"], user="root", passwd=config["database"]["password"], db="hive", charset="utf8", use_unicode=True)
    cursor = db.cursor()
    cursor.execute("SELECT name, description, url, version FROM software")
    row_count = cursor.rowcount
    soft = []
    if row_count > 0:
        for (name, description, url, version) in cursor:
            soft_item = {}
            soft_item["name"] = name
            soft_item["description"] = description
            soft_item["version"] = version
            soft_item["url"] = url

            soft.append(soft_item)
    return soft

"""
Function assemble soft_list for update procedure.
Compare income versions with server versions
"""
def soft_list(content):
    db = MySQLdb.connect(host=config["database"]["host"], user="root", passwd=config["database"]["password"], db="hive", charset="utf8", use_unicode=True)
    cursor = db.cursor()
    cursor.execute("SELECT name, description, url, version FROM software")
    row_count = cursor.rowcount
    resp = {"status": "update", "software": []}
    if row_count > 0:
        for (name, description, url, version) in cursor:
            for app in content["software"]:
                if app["name"]==name and app["version"]<version:
                    soft_item = {}
                    soft_item["name"] = name
                    soft_item["description"] = description
                    soft_item["version"] = version
                    soft_item["url"] = url
                    #soft_item["hash"] = hash

                    resp["software"].append(soft_item)
                    break
        if not resp["software"]:
            resp = {"status": "none"}
    else:
        resp = {"status": "none"}
    return resp


def get_versions():
    resp = {"status": "get_versions", "timestamp": time_stamp()}
    return jsonify(resp)


def register_drone(drone_name):
    db = MySQLdb.connect(host="localhost", user="root", passwd=config["database"]["password"], db="hive")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM drones WHERE name='"+drone_name+"'")
    db.commit()
    row_count = cursor.rowcount
    if row_count > 0:
        return 0
    else:
        cursor.execute("INSERT INTO drones (name) VALUES ('"+drone_name+"')")
        db.commit()
        return cursor.lastrowid


if __name__ == "__main__":
    app.run(host=config["server"]["host"], port=config["server"]["port"], debug=DEBUG)

