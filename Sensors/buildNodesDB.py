from config import app, db
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from heartBeat import heart_beat
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
import logging
from models import Node, Parameters, parameters_schema
import os
import pickle
from random import randint
import requests
import sys
import threading
from time import sleep


#KAFKA_IP_PORT = '127.0.0.1:53471'
KAFKA_IP_PORT = os.getenv('KAFKA_URI')


'''
Message on KAFKA Push success
'''
def onSuccess(metadata):
    print(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")


'''
Message on KAFKA Push Error
'''
def onError(e):
    print(f"Error sending message: {e}")


'''
Initial filling of the latest instance of data for all the nodes
'''
def initializeAllNodes():
    # The list of sensor-types is pre-decided
    sensor_types = ['PM10', 'Temperature', 'AQI', 'AQL', 'pH', 'Pressure', 'Occupancy', \
                    'Current', 'Frequency', 'Light_Status', 'Turbidity', 'Flowrate', 'Rain', \
                    'Energy', 'Power', 'Voltage', 'CO2', 'VOC', 'RSSI', 'Latency', 'Alarm', 'Packet_Size', \
                    'Data_Rate', 'Mac_Address', 'Node_Status']
    node_names, node_latitudes, node_longitudes, node_types, node_ips, node_ports = [], [], [], [], [], []
    unique_node_names = set()
    for sensor_type in sensor_types:
        om2m_url1 = 'https://iudx-rs-onem2m.iiit.ac.in/resource/nodes/' + sensor_type
        node_list = requests.get(om2m_url1).json()['results']
        for node in node_list:
            om2m_url2 = 'https://iudx-rs-onem2m.iiit.ac.in/resource/descriptor/' + node
            node_dict = requests.get(om2m_url2).json()
            if 'Node ID' not in node_dict:
                continue
            node_name = node_dict['Node ID']
            if node_name in unique_node_names:
                continue
            unique_node_names.add(node_name)
            node_names.append(node_name)
            node_latitudes.append(node_dict['Node Location']['Latitude'])
            node_longitudes.append(node_dict['Node Location']['Longitude'])
            node_types.append(sensor_type)
            node_ip = '192.168.36.' + str(randint(10, 50))
            node_ips.append(node_ip)
            node_ports.append(randint(8000, 9000))
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(len(node_names)):
            node_name = node_names[i]
            node_type = node_types[i]
            node_latitude = node_latitudes[i]
            node_longitude = node_longitudes[i]
            node_ip = node_ips[i]
            node_port = node_ports[i]
            new_node = Node(nodename=node_name, nodetype=node_type, nodelatitude=node_latitude, 
                            nodelongitude=node_longitude, nodeip=node_ip, nodeport=node_port)
            logging.info('Added new node to the SQLITE3 DB!')
            db.session.add(new_node)
            db.session.commit()


'''
Addition of Data to local SQLITE3 DB 
'''
def addDataToDB():
    producer = KafkaProducer(bootstrap_servers=KAFKA_IP_PORT, 
                             value_serializer=lambda m: json.dumps(m).encode('ascii'))
    consumer = KafkaConsumer(bootstrap_servers=[KAFKA_IP_PORT], group_id="demo-group", 
                             auto_offset_reset="earliest", enable_auto_commit=False,
                             consumer_timeout_ms=1000, 
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    nodes = []
    external_request = 'action_device' # Fixed by the Action Manager Module
    action_manager_module_info = []
    with app.app_context():
        while True: 
            node_info = json.loads(requests.get('http://127.0.0.1:8040/api/nodes').text)
            for node in node_info:
                nodes.append((node['id'], node['nodename'], node['nodetype']))
            logging.info('Got list of all nodes currently present!')
            for node_id, node_name, node_type in nodes:
                kafka_topic = str(node_id)
                dt_iso = datetime.now().isoformat()
                dot_index = dt_iso.index('.')
                dt_iso = dt_iso[:dot_index] + 'Z'
                om2m_url = 'https://iudx-rs-onem2m.iiit.ac.in/channels/' + node_name + '/feeds?start=' + dt_iso
                try:
                    node_data_dict = requests.get(om2m_url).json()
                    node_parameter_value = randint(20, 40)
                    if 'channel' in node_data_dict:
                        node_parameter_fields = node_data_dict['channel']
                        node_parameter_field = None
                        for node_parameter in node_parameter_fields:
                            if node_data_dict['channel'][node_parameter] == node_type:
                                node_parameter_field = node_parameter
                                break
                        temp_value = node_data_dict['feeds'][0][node_parameter_field]
                        if not isinstance(temp_value, str):
                            node_parameter_value = temp_value
                    node = db.session.get(Node, node_id)
                    consumer.subscribe(external_request)
                    # from the other team -> user_id, device_id, new_value
                    for msg in consumer:
                        logging.info('Message received from the Action Manager Module!')
                        user_id, nid, new_value = msg.value['user_id'], msg.value['device_id'], msg.value['new_value']
                        action_manager_module_info.append([int(nid), new_value])
                    for i in range(len(action_manager_module_info)):
                        if action_manager_module_info[0][0] == node_id:
                            node_parameter_value = new_value
                    content_dict = {}
                    content_dict[node_type] = node_parameter_value
                    parameter = {'content' : str(content_dict), 'node_id' : node_id}
                    future = producer.send(kafka_topic, parameter)
                    logging.info('Uploaded sensor node data to corresponding Kafta topic!')
                    future.add_callback(onSuccess)
                    future.add_errback(onError)
                    new_parameter = parameters_schema.load(parameter, session=db.session)
                    node.parameters.append(new_parameter)
                    db.session.commit()
                    logging.info('Uploaded sensor node data to SQLITE3 DB!')
                    sleep(2)
                except Exception as e:
                    logging.info('Erroneous data generated!')
                    continue
    producer.flush()
    producer.close()


'''
Dummy Data for Initialization of Sensor Nodes
'''
def initializeAllDummyNodes():
    # The list of sensor-types is pre-decided
    sensor_types = ['Temperature', 'AQI', 'pH', 'Pressure', 'Occupancy', 'Current', \
                    'Rain', 'RoomEnergy', 'Power', 'Voltage', 'SolarEnergy']
    type_name_mappings = {'Temperature' : 'WE-GS', 'AQI' : 'SR-AQ', 'pH' : 'WM-WD', \
                          'Pressure' : 'WM-WF', 'Occupancy' : 'SR-OC-GW', 'Current' : 'SR-EC', \
                          'Rain' : 'WE-VN', 'RoomEnergy' : 'SR-AC', 'Power' : 'SR-EP', \
                          'Voltage' : 'SR-EV', 'SolarEnergy' : 'SR-OC'}
    # The list of unique node locations is uploaded from a static file which has already 
    # been pre-collected from OM2M API - can't rely on it!! 
    all_node_locations = []
    with open('sensorNodeLocations', 'rb') as fp:
        all_node_locations = pickle.load(fp)
    node_names, node_types, node_locations, node_ips, node_ports = [], [], [], [], []
    for sensor_type in sensor_types:
        num_sensor_nodes = randint(10, 15)
        for node_index in range(num_sensor_nodes):
            pos = ''
            if node_index < 10:
                pos = '0' + str(node_index)
            else:
                pos = str(node_index)
            node_location = all_node_locations[randint(0, len(all_node_locations) - 1)]
            node_name = type_name_mappings[sensor_type] + '-' + node_location + '-' + pos
            node_names.append(node_name)
            node_types.append(sensor_type)
            node_locations.append(node_location)
            node_ips.append('192.168.10.' + str(randint(10, 80)))
            node_ports.append(randint(8100, 8900))
    with app.app_context():
        db.drop_all()
        db.create_all()
        for i in range(len(node_names)):
            new_node = Node(nodename=node_names[i], nodetype=node_types[i], nodelocation=node_locations[i], 
                            nodeip=node_ips[i], nodeport=node_ports[i])
            logging.info('Added new sensor node to the SQLITE3 DB!')
            db.session.add(new_node)
            db.session.commit()


'''
Filling up of Dummy Data to the local SQLITE3 DB
'''
def addDummyDataToDB():
    producer = KafkaProducer(bootstrap_servers=KAFKA_IP_PORT, 
                             value_serializer=lambda m: json.dumps(m).encode('ascii'))
    consumer = KafkaConsumer(bootstrap_servers=[KAFKA_IP_PORT], group_id="demo-group", 
                             auto_offset_reset="earliest", enable_auto_commit=False,
                             consumer_timeout_ms=1000, 
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    nodes = []
    external_request = 'action_device' # Fixed by the Action Manager Module
    action_manager_module_info = []
    with app.app_context():
        while True: 
            node_info = json.loads(requests.get('http://127.0.0.1:8040/api/nodes').text)
            for node in node_info:
                nodes.append((node['id'], node['nodename'], node['nodetype']))
            logging.info('Got list of all nodes currently present!')
            for node_id, node_name, node_type in nodes:
                kafka_topic = str(node_id)
                dt_iso = datetime.now().isoformat()
                try:
                    node_parameter_value = -1
                    if node_type == 'AQI':
                        node_parameter_value = randint(20, 26) # > 25
                    elif node_type == 'SolarEnergy':
                        node_parameter_value = randint(22, 38) # > 35
                    elif node_type == 'RoomEnergy':
                        node_parameter_value = randint(21, 28) # > 26
                    else:
                        node_parameter_value = randint(20, 40) # > 36
                    node = db.session.get(Node, node_id)
                    consumer.subscribe(external_request)
                    # from the other team -> user_id, device_id, new_value
                    for msg in consumer:
                        logging.info('Message received from the Action Manager Module!')
                        user_id, nid, new_value = msg.value['user_id'], msg.value['device_id'], msg.value['new_value']
                        action_manager_module_info.append([int(nid), new_value])
                    for i in range(len(action_manager_module_info)):
                        if action_manager_module_info[0][0] == node_id:
                            node_parameter_value = new_value
                    content_dict = {}
                    content_dict[node_type] = node_parameter_value
                    parameter = {'content' : str(content_dict), 'node_id' : node_id}
                    future = producer.send(kafka_topic, parameter)
                    logging.info('Uploaded sensor node data to corresponding Kafta topic!')
                    future.add_callback(onSuccess)
                    future.add_errback(onError)
                    new_parameter = parameters_schema.load(parameter, session=db.session)
                    node.parameters.append(new_parameter)
                    db.session.commit()
                    logging.info('Uploaded sensor node data to SQLITE3 DB!')
                    sleep(1)
                except Exception as e:
                    logging.info('Some unforeseen error!')
                    continue
    producer.flush()
    producer.close()


'''
The controller function of the script that calls the desired functions
'''
def main():
    module_name = 'sensor_manager'
    t = threading.Thread(target=heart_beat, args=(module_name,))
    t.daemon = True
    t.start()
    log = 'sensormanager.log'
    logging.basicConfig(filename=log, filemode='w', level=logging.DEBUG, \
                        format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    #initializeAllNodes()
    initializeAllDummyNodes()
    logging.info('Initialized all the sensor nodes!')
    #addDataToDB()
    addDummyDataToDB()


if __name__ == '__main__':
    main()
