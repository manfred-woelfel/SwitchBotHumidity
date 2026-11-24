import sys
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

threshold_temperature = 16
threshold_humidity = 60

mon = getattr(sys, "monitoring", None)
debug = mon and mon.get_tool(mon.DEBUGGER_ID)
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


#db = firestore.get_firestore_client()
#STATE_DOC = db.collection("smart_home").document("tatami_ac_state")

body = devices_data.get("body", {})

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

def setAC(ids, temperature, power, mode=ACMode.AUTO, fan_speed=ACFanSpeed.AUTO):
    payload = {
        "command": "setAll",
        "parameter": f"{temperature},{mode},{fan_speed},{power}",
        "commandType": "command"
    }
      
    for id in ids: 
        print(f"{id}: {temperature}°C, {mode.name}, fan={fan_speed.name}, {power}")         
        if not debug:
            print(debug)
            res = requests.post(commandURL(id), headers=apiHeader, json=payload)
            print(res.json())

remotes = body.get("infraredRemoteList", [])
aircons = list(filter(lambda r: "Air Conditioner" in r.get("remoteType", ""), remotes))
devices = body.get("deviceList", [])
hub_names = dict(map(lambda d: (d["deviceId"], d["deviceName"]), devices))
# Filter to only physical Hubs, then map each Hub to its list of controlled remotes
hubs = filter(lambda d: "Hub" in d.get("deviceType", ""), devices)
mm = dict(map(
    lambda h: (
        h["deviceName"],
        list(map(
            lambda r: r["deviceId"],
            filter(lambda r: r.get("hubDeviceId") == h["deviceId"], aircons)
        ))
    ),
    hubs
))

for device in devices:
    hub_id = device["deviceId"]
    hub_name = device["deviceName"]
    id = mm[hub_name]
    print(hub_name)
    data = requests.get(f"{devices_url}/{hub_id}/status", headers=apiHeader)
    status_body = data.json().get('body', {})
    print(status_body)
    if (status_body):
        humidity = status_body.get('humidity')
        temperature = status_body.get('temperature')
        light_level = status_body.get('lightLevel')

        setAC(id, threshold_temperature,
            "on" if humidity > threshold_humidity else "off",
            ACMode.HEAT if temperature < threshold_temperature else ACMode.AUTO)
    print()
