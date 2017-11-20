"""
This script requires requests library. You can install it using command below:

pip install requests
"""
import os

import requests

if __name__ == '__main__':
    fp = open("scenario_schema_error.xml")
    r = requests.post("https://om.vecnet.org/ts_om/restValidate/", data=fp.read())
    fp.close()
    result = r.json()
    if result["result"] == 0:
        print("Success!")
    else:
        for message in result["om_output"]:
            print message
