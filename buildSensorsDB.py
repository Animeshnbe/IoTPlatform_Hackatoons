import ast
from config import app, db
from datetime import datetime
from heartBeat import heart_beat
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from models import Sensor, Parameters, parameters_schema
from random import randint
import requests
import threading
from time import sleep
import xmltodict


'''
Message on KAFKA Push success
'''
def on_success(metadata):
    print(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")


'''
Message on KAFKA Push Error
'''
def on_error(e):
    print(f"Error sending message: {e}")


'''
Initializing the Sensors DB - helps in creating the schema.
'''
def buildSensorDB():
    SENSORS_PARAMETERS = [
        {
            'sensorname' : 'Sensor1', 
            'sensortype' : 'Pressure', 
            'sensorlatitude' : 10, 
            'sensorlongitude' : 20, 
            'sensorip' : '127.0.0.1', 
            'sensorport' : 8030, 
            'sensoractive' : True, 
            'parameters' : [
                (1, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor2', 
            'sensortype' : 'Motion', 
            'sensorlatitude' : 15, 
            'sensorlongitude' : 20, 
            'sensorip' : '127.0.0.2', 
            'sensorport' : 8032, 
            'sensoractive' : True, 
            'parameters' : [
                (2, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor3', 
            'sensortype' : 'AirQuality', 
            'sensorlatitude' : 45, 
            'sensorlongitude' : 12, 
            'sensorip' : '127.0.0.3', 
            'sensorport' : 8034, 
            'sensoractive' : True, 
            'parameters' : [
                (3, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor4', 
            'sensortype' : 'Temperature', 
            'sensorlatitude' : 20, 
            'sensorlongitude' : 40, 
            'sensorip' : '127.0.0.4', 
            'sensorport' : 8036, 
            'sensoractive' : True, 
            'parameters' : [
                (4, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor5', 
            'sensortype' : 'Humidity', 
            'sensorlatitude' : 40, 
            'sensorlongitude' : 20, 
            'sensorip' : '127.0.0.5', 
            'sensorport' : 8038, 
            'sensoractive' : True, 
            'parameters' : [
                (5, '', '2023-04-08 07:15:03'), 
            ], 
        }, 
        {
            'sensorname' : 'Sensor6', 
            'sensortype' : 'Light', 
            'sensorlatitude' : 24, 
            'sensorlongitude' : 56, 
            'sensorip' : '127.0.0.6', 
            'sensorport' : 8039, 
            'sensoractive' : True, 
            'parameters' : [
                (6, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor7', 
            'sensortype' : 'Sound', 
            'sensorlatitude' : 30, 
            'sensorlongitude' : 20, 
            'sensorip' : '127.0.0.7', 
            'sensorport' : 8037, 
            'sensoractive' : True, 
            'parameters' : [
                (7, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor8', 
            'sensortype' : 'Pressure', 
            'sensorlatitude' : 15, 
            'sensorlongitude' : 20, 
            'sensorip' : '127.0.1.1', 
            'sensorport' : 8030, 
            'sensoractive' : True, 
            'parameters' : [
                (8, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor9', 
            'sensortype' : 'Motion', 
            'sensorlatitude' : 25, 
            'sensorlongitude' : 100, 
            'sensorip' : '127.0.1.2', 
            'sensorport' : 8032, 
            'sensoractive' : True, 
            'parameters' : [
                (9, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor10', 
            'sensortype' : 'AirQuality', 
            'sensorlatitude' : 45, 
            'sensorlongitude' : 122, 
            'sensorip' : '127.0.1.3', 
            'sensorport' : 8034, 
            'sensoractive' : True, 
            'parameters' : [
                (10, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor11', 
            'sensortype' : 'Temperature', 
            'sensorlatitude' : 29, 
            'sensorlongitude' : 102, 
            'sensorip' : '127.0.1.4', 
            'sensorport' : 8036, 
            'sensoractive' : True, 
            'parameters' : [
                (11, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor12', 
            'sensortype' : 'Humidity', 
            'sensorlatitude' : 44, 
            'sensorlongitude' : 25, 
            'sensorip' : '127.0.1.5', 
            'sensorport' : 8038, 
            'sensoractive' : True, 
            'parameters' : [
                (12, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
        {
            'sensorname' : 'Sensor13', 
            'sensortype' : 'Light', 
            'sensorlatitude' : 64, 
            'sensorlongitude' : 156, 
            'sensorip' : '127.0.1.6', 
            'sensorport' : 8039, 
            'sensoractive' : True, 
            'parameters' : [
                (13, '', '2023-04-08 07:15:03'), 
            ], 
        }, 
        {
            'sensorname' : 'Sensor14', 
            'sensortype' : 'Sound', 
            'sensorlatitude' : 18, 
            'sensorlongitude' : 14, 
            'sensorip' : '127.0.1.7', 
            'sensorport' : 8037, 
            'sensoractive' : True, 
            'parameters' : [
                (14, '', '2023-04-08 07:15:03'),   
            ], 
        }, 
    ]
    with app.app_context():
        db.drop_all()
        db.create_all()
        for data in SENSORS_PARAMETERS:
            new_sensor = Sensor(sensorname=data.get('sensorname'), sensortype=data.get('sensortype'), 
                                sensorlatitude=data.get('sensorlatitude'), 
                                sensorlongitude=data.get('sensorlongitude'), 
                                sensorip=data.get('sensorip'), sensorport=data.get('sensorport'))
            for _, content, timestamp in data.get('parameters', []):
                new_sensor.parameters.append(Parameters(content=content, 
                                             timestamp=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'), ))
            db.session.add(new_sensor)
            db.session.commit()


'''
Adding data generated by OM2M to the Sensors DB.
This function also takes input from the Kafka topic 'action_device' and 
modifies values before pushing them into Kafka server and the SQLITE3 DB.
'''
def addDataToDB():
    om2m_url = 'http://127.0.0.1:5089/'
    om2m_username = 'admin'
    om2m_password = 'admin'
    om2m_csebase = '~/in-cse/'
    om2m_resource_path = 'in-name/AE-TEST/Node-1/Data/la'
    om2m_auth = requests.auth.HTTPBasicAuth(om2m_username, om2m_password)
    producer = KafkaProducer(bootstrap_servers = "127.0.0.1:54351", 
                             value_serializer=lambda m: json.dumps(m).encode('ascii'))
    consumer = KafkaConsumer(bootstrap_servers=["127.0.0.1:54351"], group_id="demo-group", 
                             auto_offset_reset="earliest", enable_auto_commit=False,
                             consumer_timeout_ms=1000, 
                             value_deserializer=lambda m: json.loads(m.decode('ascii')))
    external_request_topic = 'action_device'
    new_values_dict = {}
    with app.app_context():
        while True:
            om2m_response = requests.get(om2m_url + om2m_csebase + om2m_resource_path, auth=om2m_auth)
            timestamp = datetime.now().replace(microsecond=0).isoformat(' ')
            sensor_info = requests.get('http://127.0.0.1:8046/api/sensors')
            sensor_info = json.loads(sensor_info.text)
            active_sensors = []
            for sensor in sensor_info:
                if sensor['sensoractive']:
                    active_sensors.append(sensor['id'])
                    if sensor['id'] not in new_values_dict:
                        new_values_dict[sensor['id']] = None
            try:
                dict_obj = xmltodict.parse(om2m_response.text)
                data = dict_obj['m2m:cin']
                sensor_id = randint(1, len(active_sensors))
                sensor_id = active_sensors[sensor_id - 1]
                kafka_topic = str(sensor_id)
                sensor = db.session.get(Sensor, sensor_id)
                consumer.subscribe(external_request_topic)
                temp_list = ast.literal_eval(data['con'])
                # from the other team -> user_id, device_id, new_value
                for msg in consumer:
                    print ('From other module!')
                    print (msg.value)
                    user_id, sid, new_value = msg.value['user_id'], msg.value['device_id'], msg.value['new_value']
                    if sid == sensor_id:
                        temp_list[2] = msg.value['new_value']
                        data['con'] = str(temp_list)
                if sensor_id not in new_values_dict:
                    new_values_dict[sensor_id] = None
                if new_values_dict[sensor_id] is not None:
                    temp_list[2] = new_values_dict[sensor_id]
                    data['con'] = str(temp_list)   
                parameter = {'content' : str(data), 'sensor_id' : sensor_id}
                future = producer.send(kafka_topic, parameter)
                future.add_callback(on_success)
                future.add_errback(on_error)
                new_parameter = parameters_schema.load(parameter, session=db.session)
                sensor.parameters.append(new_parameter)
                db.session.commit()
                sleep(3)
            except Exception as e:
                print ('Erroneous Data!')
                continue
    producer.flush()
    producer.close()


'''
The controller function of the script
'''
def main():
    module_name = 'SensorManager'
    t = threading.Thread(target=heart_beat, args=(module_name,))
    t.daemon = True
    t.start()
    buildSensorDB()
    addDataToDB()


if __name__ == '__main__':
    main()
