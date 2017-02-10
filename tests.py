import lib
import os


resp = lib.first_request()

while resp["action"] != "none":
    if resp["action"] == "get_current_versions":
        resp=lib.ver_info()
    if resp["action"] == "update":
        for app in resp["software"]:
            lib.download(app["update_url"])
            if lib.hash_control(app["update_url"], app["hash"]):
                lib.archive_unzip_update(os.path.basename(app["update_url"]))





