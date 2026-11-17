import json
import os
import time
import hashlib
import hmac
import base64
import uuid
import requests

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


devices_url = "https://api.switch-bot.com/v1.1/devices"
response = requests.get(devices_url, headers=apiHeader)
devices_data = response.json()

# Print all infrared remotes to find your Air Conditioner's deviceId
for ir_device in devices_data.get('body', {}).get('infraredRemoteList', []):
    print(f"Name: {ir_device['deviceName']} | Type: {ir_device['remoteType']} | ID: {ir_device['deviceId']}")

for dev in devices_data.get("body", {}).get("deviceList", []):
    print(f"Name: {dev['deviceName']} | Type: {dev.get('deviceType')} | ID: {dev['deviceId']}")
    if dev.get("deviceType") == "Hub 2":
        hub2_device_id = dev["deviceId"]

status_url = f"{devices_url}/{hub2_device_id}/status"

res = requests.get(status_url, headers=apiHeader)
data = res.json()

# Print the full status response
print(data)

# Extract specific sensor readings
status_body = data.get('body', {})
humidity = status_body.get('humidity')
temperature = status_body.get('temperature')
light_level = status_body.get('lightLevel')




def diy():
    light_device_id = "01-202611081937-37986025"
    command_url = f"{devices_url}/{light_device_id}/commands"
    payload = {
        "command": "turnOff",
        "parameter": "default",
        "commandType": "command"
    }
    res = requests.post(command_url, headers=apiHeader, json=payload)
    print(res.json())
    return res