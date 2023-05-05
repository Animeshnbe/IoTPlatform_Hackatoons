from kafka import KafkaConsumer
import requests
import json
import time
from mongo_utility import MongoUtility
from bson import json_util
import threading
from dotenv import load_dotenv
import os
import datetime
from communication_api import monitor
from loggingUtility import logger_func, init_logging
from sshUtility import SSHUtil
from kafkautilities import kafka_consume, kafka_produce

# logger = logger_func()
logger = init_logging()

load_dotenv()  # take environment variables from .env.

threshold = 12

# kafkaPort = os.getenv("kafkaPort")

# kafkaAddress = os.getenv("kafkaAddress") + ":{}".format(kafkaPort)  # ProducerIP : ProducerPort

kafkaAddress = os.getenv("KAFKA_URI")

collection_name = os.getenv("collection_name")
database_name = os.getenv("database_name")
app_runtimes_collection_name = os.getenv("app_runtimes_collection_name")

fault_tolerance_topic = os.getenv("fault_tolerance_topic")

# mongo_port = int(os.getenv("mongo_port"))
# mongo_host = os.getenv("mongo_host")

mongo_uri = os.getenv("MONGO_DB")

module_dict = dict()
module_status = dict()

mongo_utility = MongoUtility(mongo_uri)


def kafka_fault_tolerance(module_name):
    try:
        module_json = dict(name=module_name)
        record = mongo_utility.find_json(module_json, database_name, collection_name)
        print("record : ", record)
        module_port = record[0].get("port", "")
        message = {
            'module_name': module_name,
            'port': int(module_port)
        }
        print("Kafka Fault Tolerance Message : ", message)
        logger.debug("Kafka Fault Tolerance Message : " + str(message))
        print("Topic : ", fault_tolerance_topic)
        kafka_produce(kafkaAddress, fault_tolerance_topic, message)
        print("Kafka Fault Tolerance Topic created")
        logger.info("Kafka Fault Tolerance Topic created")
    except Exception as e:
        print("Error : ", e)
        logger.error(e)


def sample_app_request(app_name, app_number):
    try:
        module_json = dict(name="deployer")
        record = mongo_utility.find_json(module_json, database_name, collection_name)
        print("Mongo Record : ", record)
        app_ip = record[0].get("ip", "")
        app_port = record[0].get("port", "")
        url = "http://{}:{}/restart_service".format(app_ip, app_port)
        print("URL : ", url)
        # http: // < deployer_ip >: 8888 / restart_service
        data = {
            "name": app_name+"_app",
            "username": app_number,
            "type": "app_runtimes"
        }

        print("data : ", data)
        response = requests.post(url, json=data)
        print("APP POST Response : ", response)
        logger.debug("APP POST Response : " + str(response))

    except Exception as e:
        print("Error : ", e)
        logger.error(e)


def fetch_status():
    for message in monitor():
        # logger.info("Message : " + str(message))
        module_dict[message['moduleName']] = message['currentTime']


def fetch_module_status():
    t = threading.Thread(target=fetch_status)
    t.daemon = True
    t.start()

    # print("Inside fetch_module_status")
    down = []

    while True:
        if len(module_dict) > 0:
            for module in module_dict.keys():
                # print("Module : ", module)
                current_time = datetime.datetime.utcnow()
                date_time_obj = datetime.datetime.strptime(module_dict[module], '%Y-%m-%d %H:%M:%S.%f')
                logger.info("current_time : " + str(current_time))
                # print("date_time_obj : ", date_time_obj)
                diff = (current_time - date_time_obj).total_seconds()
                logger.info("Monitor time Difference:" + str(diff))
                if diff > threshold:
                    if module in down:
                        continue
                    else:
                        module_status[module] = False
                        if module.startswith("app"):
                            words = module.split("_")
                            app_name = words[-2]
                            sample_app_request(app_name, words[1])
                        else:
                            kafka_fault_tolerance(module)
                        # obj = SSHUtil()
                        # a, b = obj.execute_command(["python3 hello.py"], "10.2.136.254", "aman_2110")

                        down.append(module)
                else:
                    if module in down:
                        down.remove(module)

                    # print(module + " up")
                    module_status[module] = True
                # if mongo_utility.check_document(database_name, json_data, collection_name):

                if module.startswith("app"):
                    json_data = {'status': module_status[module]}
                    logger.info("JSON TYPE : " + str(json_data))
                    words1 = module.split("_")
                    sample_app_name = words1[1] + "_" + words1[-2] + "_" + words1[-1]
                    print("Sample App Name : ", sample_app_name)
                    mongo_utility.update_app_one_field(sample_app_name, module_status[module], database_name,
                                                       app_runtimes_collection_name)
                else:
                    json_data = {'status': module_status[module]}
                    logger.info("JSON TYPE : " + str(json_data))

                    mongo_utility.update_one_field(module, module_status[module], database_name, collection_name)

        time.sleep(5)


def node_monitoring():
    try:
        send_logs_thread = threading.Thread(target=fetch_module_status)
        send_logs_thread.daemon = True
        send_logs_thread.start()

    except Exception as e:
        print(e)


# def fetch_nodes_status():
#     try:
#         kafka_consumer = KafkaConsumer(bootstrap_servers=[kafkaAddress, kafkaAddress1], auto_offset_reset='latest',
#                                        enable_auto_commit=True, value_deserializer=lambda x: x.decode('utf-8'))
#         kafka_consumer.subscribe(topics=["nodestats3"])
#         print(kafka_consumer.subscription())
#         mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
#         for stats in kafka_consumer:
#             node_details = dict()
#             data = stats.value
#             stats = json.loads(data)
#             node_details['nodeID'] = stats["nodeID"]
#             node_details["username"] = stats["username"]
#             node_details["password"] = stats["password"]
#             node_details["free_cpu"] = float(stats["free_cpu"])
#             node_details["free_memory"] = float(stats["free_memory"])
#             node_details["number_of_events_per_sec"] = int(stats["number_of_events_per_sec"])
#             node_details["free_RAM"] = float(stats["free_RAM"])
#             node_details["temperature"] = float(stats["temperature"])
#             node_details["n_cores"] = int(stats["n_cores"])
#             node_details["timestamp"] = time.time()
#             json_data = {'nodeID': node_details['nodeID']}
#             if mongo_utility.check_document(database_name, json_data, collection_name):
#                 mongo_utility.update_one(json_data, node_details, database_name, collection_name)
#                 print(node_details['nodeID'], '- updated record into registry.')
#             else:
#                 rec = mongo_utility.insert_one(node_details, database_name, collection_name)
#                 print(node_details['nodeID'], '- new record inserted into registry with id :', rec)
#
#     except Exception as e:
#         print(e)
#
#
def send_node_modules():
    record = mongo_utility.find_all(database_name, collection_name)
    data = {}
    server_load = []

    for x in record:
        if x["status"] == "up":
            server_load.append(x)

    data["n_servers"] = len(server_load)
    data["server_load"] = server_load
    res = json.dumps(data, default=json_util.default)
    return res
