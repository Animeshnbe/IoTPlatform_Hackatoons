#!/Users/imrp26/.pyenv/shims/python3

import json
from kafka import KafkaProducer
import requests
from time import sleep
import xmltodict


om2m_url = 'http://127.0.0.1:5089/'
om2m_username = 'admin'
om2m_password = 'admin'
om2m_csebase = '~/in-cse/'
om2m_resource_path = 'in-name/AE-TEST/Node-1/Data?rcn=4'
om2m_auth = requests.auth.HTTPBasicAuth(om2m_username, om2m_password)
om2m_response = requests.get(om2m_url + om2m_csebase + om2m_resource_path, auth=om2m_auth)
dict_obj = xmltodict.parse(om2m_response.text)
data = dict_obj['m2m:cnt']['m2m:cin']
tb_url = 'http://localhost:9090/api/v1/'
tb_access_token = 'A1_TEST_TOKEN'
tb_device_id = '0eb6fff0-c0ae-11ed-8a7c-a57dec691272'

mapping = {'rn' : 'rn', 'ty' : 'ty', 'ri' : 'ri', 'pi' : 'pi', 
           'ct' : 'ct', 'lt' : 'lt', 'lbl' : 'lbl', 'st' : 'st', 
           'cnf' : 'cnf', 'cs' : 'cs', 'con' : 'con'}
headers = {'Content-Type': 'application/json', 'X-Authorization': 'Bearer ' + tb_access_token,
           'Accept': 'application/json'}
producer = KafkaProducer(bootstrap_servers=['localhost:29092'], api_version=(0, 10, 1))

for data1 in data:
    print (data1)
    payload = {}
    for om2m_name, tb_name in mapping.items():
        if om2m_name in data1:
            payload[tb_name] = data1[om2m_name]
    url = tb_url + tb_access_token + '/telemetry'
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print ('Data sent to ThingsBoard : ' + str(payload))
    else:
        print ('Error in sending data to ThingsBoard : ' + str(response.status_code))
    #thingsboard_url = 'http://{YOUR_THINGSBOARD_HOST}/api/v1/{ACCESS_TOKEN}/telemetry/{DEVICE_ID}'
    thingsboard_url = tb_url + tb_access_token + '/telemetry/' + tb_device_id
    tb_response = requests.get(thingsboard_url, headers=headers)
    producer.send('foobar', json.dumps(payload).encode('utf-8'))
    sleep(3)
    print ('Message sent :', payload)
