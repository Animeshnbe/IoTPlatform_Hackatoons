import requests
import json

SENSOR_MGR = ''
GLOBAL_KAFKA = ''
GLOBAL_DB = ''

def check_sensors(sensors_list):
    pass

def get_sensors_by_loc(location, action='on'):
    return ['ac1','ac2']

def get_sensors_by_cat(category='switch', action='on'):
    return ['ac1', 'ac2']


def add_subscription(username,app_name):
    res = requests.post(
    url=f"{GLOBAL_KAFKA}:18082/consumers/test_group",
    data=json.dumps({
        "name": username+"_"+app_name,
        "format": "json",
        "auto.offset.reset": "earliest",
        "auto.commit.enable": "false",
        "fetch.min.bytes": "1",
        "consumer.request.timeout.ms": "10000"
    }),
    headers={"Content-Type": "application/vnd.kafka.v2+json"}).json()

    print(res)

def get_data(device_cat):
    fetch_device_instance(device_cat)


def set_action(action_name):
    validate_action(action_name, device_name)


