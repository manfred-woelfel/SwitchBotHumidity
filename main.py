import json
import os
import time
import hashlib
import hmac
import base64
import uuid
import requests

from enum import IntEnum

class ACMode(IntEnum):
    AUTO = 1
    COOL = 2
    DRY = 3
    FAN = 4
    HEAT = 5

class ACFanSpeed(IntEnum):
    AUTO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4

apiHeader = {}
token = os.environ["SWITCHBOT_TOKEN"].strip()
secret = os.environ["SWITCHBOT_SECRET"].strip()
nonce = uuid.uuid4()
t = int(round(time.time() * 1000))
string_to_sign = bytes('{}{}{}'.format(token, t, nonce), 'utf-8')
secret = bytes(secret, 'utf-8')

sign = base64.b64encode(hmac.new(secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

apiHeader['Authorization']=token
apiHeader['Content-Type']='application/json'
apiHeader['charset']='utf8'
apiHeader['t']=str(t)
apiHeader['sign']=str(sign, 'utf-8')
apiHeader['nonce']=str(nonce)

api = "https://api.switch-bot.com/v1.1/" 
devices_url = api + "/devices"
response = requests.get(devices_url, headers=apiHeader)
devices_data = response.json()

ir_list = devices_data.get("body", {}).get("infraredRemoteList", [])

ac_device = next(
    filter(lambda d: d.get("remoteType") == "Air Conditioner", ir_list)
)

ac_device_id = ac_device["deviceId"]
print(ascii(ac_device))
print(ac_device_id)

def getHub2Device():
    return next(
        map(
            lambda d: d["deviceId"],
            filter(lambda d: d.get("deviceType") == "Hub 2", devices_data.get("body", {}).get("deviceList", []))
        )
    )

def commandURL(id):
    return f"{devices_url}/{id}/commands"
    
def getCommands(id):
        payload = {
            "command": "turnOff",
            "parameter": "default",
            "commandType": "command"
        }
        res = requests.post(commandURL(id), headers=apiHeader, json=payload)
        print(res.json())
        return res

def diy(id):
    payload = {
        "command": "turnOff",
        "parameter": "default",
        "commandType": "command"
    }
    res = requests.post(commandURL(id), headers=apiHeader, json=payload)
    print(res.json())
    return res

def setAC(id, temperature, power, mode=ACMode.AUTO, fan_speed=ACFanSpeed.AUTO):
    url = commandURL(id)

    payload = {
        "command": "setAll",
        "parameter": f"{temperature},{mode},{fan_speed},{power}",
        "commandType": "command"
    }   
    print(payload)         
    res = requests.post(commandURL(id), headers=apiHeader, json=payload)
    print(res.json())
    return res

data = requests.get(f"{devices_url}/{getHub2Device()}/status", headers=apiHeader)
status_body = data.json().get('body', {})
humidity = status_body.get('humidity')
temperature = status_body.get('temperature')
light_level = status_body.get('lightLevel')

threshold_temperature = 20
threshold_humidity = 75
setAC(ac_device_id, threshold_temperature,
      "on" if humidity > threshold_humidity else "off",
      ACMode.DRY if temperature > threshold_temperature else ACMode.HEAT,
      ACFanSpeed.HIGH)

