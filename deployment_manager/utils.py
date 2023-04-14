import flask
import threading
import requests
import json
import os
import io
import pymongo
import paramiko
import uuid
import shutil
import subprocess
from azure.storage.blob import BlobServiceClient
import zipfile
from loggingUtility import logger_func

logger = logger_func()

# logger.info("The program is working as expected")
# logger.warning("The program may not function properly")
# logger.error("The program encountered an error")
# logger.critical("The program crashed")

import configparser
config = configparser.ConfigParser()
config.read('.env')
configs = config['local']

from mockdata import produce
from kafka import KafkaConsumer

import pymongo
client = pymongo.MongoClient(configs["MONGO_CONN_STRING"])
# client = pymongo.MongoClient(configs["MONGO_URI"],int(configs["MONGO_PORT"]))
db = client['IAS_Global']

from time import sleep

deploy_requests = []

def get_schedules(consumer):
    # Consume messages from a topic
    for message in consumer:
        deploy_requests.append(message.value)

def scheduler_consumer():
    # while(1):
    #     if len(deploy_requests)>0:
    #         deploy_request = deploy_requests.pop(0)
    #         print(deploy_request)
    #         deploy_util(deploy_request['user'],deploy_request['appname'])
    #     sleep(0.5)

    # consumer = KafkaConsumer('sch_dep', bootstrap_servers=[configs['KAFKA_URI']],
    #                             value_deserializer=lambda x: json.loads(x.decode('utf-8')))


    # t1 = threading.Thread(target = get_schedules, args=(consumer,))
    # t1.start()
    print(configs["KAFKA_URI"])
    consumer = KafkaConsumer('sch_dep', bootstrap_servers=[configs["KAFKA_URI"]],
                                value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    # consumer.seek(0,0)
    print("Waiting...")
    for message in consumer:
        # topic_info = f"topic: {message.topic} ({message.partition}|{message.offset})"
        # data = json.loads(message.value.decode('utf-8'))
        # message_info = f"key: {message.key}, {data}"
        # print(f"{topic_info}, {message_info}")
        print(message.value)
        m = message.value
        deploy_util(m['user'],m['appname'])
        # consumer.commit()

def download_zip(container, zip_file_name,extract=False):
    logger.info("ARGS +++++ %s %s",container,zip_file_name)
    connect_str = "DefaultEndpointsProtocol=https;AccountName=aman0ias;AccountKey=ejuMHDXoYsp4ktNpndJTqrC0QXgEi7DCv0cJiK94R6ZhMYZa+VmKnYcTNv3T6qIc/qoYnnZbGZPg+AStGotFJA==;EndpointSuffix=core.windows.net"

    container_name = container         #container name
    blob_name = zip_file_name          #zip file name

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    blob_data = io.BytesIO()
    blob_client.download_blob().download_to_stream(blob_data)

    if not os.path.exists("../uploads/"+container):
        os.mkdir("../uploads/"+container)

    if extract:
        os.chdir("../uploads/"+container)
        with zipfile.ZipFile(blob_data) as zip_file:
            zip_file.extractall("../uploads/"+container)
    else:
        with open("../uploads/"+container+"/"+zip_file_name, "wb") as f:
            f.write(blob_data.getbuffer())

def generate_docker(fp,service, sensor_topic, controller_topic, username):
    df = open(fp+'/Dockerfile', 'w')
    pip = service['requirements']
    filename = service['filename']
    
    dependency = service['dependency']   #other service topics

    for ser in dependency['platform']:
        deploy_util(ser,username)
        # pass

    for ser in dependency['bundle']:
        if dependency['bundle'][ser]=="True":
            subprocess.run("docker run -d --net="+username+"_net --name "+ser+" "+ser)
        else:
            out=os.system('docker build -t '+ser+':latest '+ser+'/')
            # logger.info("Build result: ",out)
            if out!=0:
                logger.error("Some error occured starting your service: "+ser)
                os.remove('Dockerfile')
                return
            subprocess.run("docker run -d --net="+username+"_net --name "+ser+" "+ser)
    baseimage = 'FROM '+service["base"]+':latest\n'
    df.write(baseimage)
    df.write('\n')

    if service["base"]=="alpine":
        env = 'RUN apk update && apk add python3 py3-pip curl unzip\n'
    else:
        env = 'RUN apt-get update && apt-get install -y python3 python3-pip\n'
    df.write(env)

    for k,v in service["env"].items():
        df.write("ENV "+k+"="+v+'\n')
    
    with open(fp+'/requirements.txt', 'w') as f:
        for package in pip:
            f.write(package+"\n")


    df.write('ADD . ./home\n') # COPY SRC
    df.write('CMD cd home\n')
    df.write('RUN pip3 install --no-cache-dir -r ./home/requirements.txt\n')


    # keyword_args = (' ').join(dependency)
    runcmd = 'ENTRYPOINT python3 -u /home/' + filename + ' ' + (' ').join(sensor_topic) + ' ' + (' ').join(controller_topic) # + " " + keyword_args
    df.write(runcmd.rstrip())
    df.close()

def deploy_util(app_name,username,port=None):
    # 1 verify user
    found = db['users'].find_one({'username':username})
    app_found = db['app_uploads'].find_one({'filename':app_name})
    print("Request received... ")
    if not found:
        return {"status":0,"message":"No such user"}
    if not app_found:
        return {"status":0,"message":"No such app"}
    elif 'admin' not in found["role"] and app_found["username"]!=username:
        return {"status":0,"message":"Invalid user"}
    
    print("Deploying... ")
    username = app_found["username"].lower()
    # same docker network as node manager
    resp = requests.post("http://localhost:8887",json={"port":port}).json()
    if resp["msg"]!="OK":
        return {"status":0,"message":resp["msg"]}
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=resp["ip"],username=resp["username"],password=resp["password"])
    ftp_client=ssh.open_sftp()
    try:
        ftp_client.stat("uploads/"+app_name.lower())
        print(True)
    except FileNotFoundError:
        ssh.exec_command("mkdir -p uploads/"+app_name.lower())
    ftp_client.put("init.py","./uploads/"+app_name.lower()+"/init.py")
    # Replace the foll. with sensor manager caller
    ftp_client.put("dummy.json","./uploads/"+app_name.lower()+"/dummy.json")
    ftp_client.put("mockdata.py","./uploads/"+app_name.lower()+"/mockdata.py")
    print("Placed starter files...")
    if port is not None:
        if "admin" not in found.role:
            return {"status":0, "message":"Starting service not allowed"}
        shutil.make_archive(app_name, 'zip', app_name)
        ftp_client.put("../services/"+app_name+".zip","./uploads/"+app_name.lower()+"/"+app_name+".zip")
        os.remove("../services/"+app_name+".zip")
    else:
        # 2 fetch code artifacts
        download_zip(username,app_name+".zip")
        print("Downloaded files...")
        ftp_client.put("../uploads/"+username+"/"+app_name+".zip","./uploads/"+app_name.lower()+"/"+app_name+".zip")
        print("Sent the app...")
    ftp_client.close()
    ssh.exec_command("pip install requests")

    _, stdout, stderr = ssh.exec_command("cd uploads/"+app_name.lower()+" && python3 init.py "+app_name.lower()+" "+username+" "+configs["KAFKA_URI"])
    print("SSH OUT>>>>>>>>>>>>>", stdout.read().decode())
    print("SSH ERR>>>>>>>>>>>>>", stderr.read().decode())
    result = json.loads(stdout.read().decode())
    # shutil.copy
    # result = {'status':1,'message':"Deployed Successfully"}
    if result['status']==1:
        if port is not None:
            collection = "services"
        else:
            collection = "app_runtimes"
        if collection in db.list_collection_names():
            print("The collection already exists.")
        else:
            # Create the collection
            collection = db.create_collection(collection)
        collection = db[collection]
        mydata = {"node_id": result["runtime_id"], "app": app_name, "deployed_by":username, "status": True,
                  "volume":result["vol"], "machine":{"ip":resp["ip"], "username":resp["username"],"password":resp["password"]}}
        collection.insert_one(mydata)

    return result

def deploy_util2(app_name,username,port=None):
    # 1 verify user
    found = db['users'].find_one({'username':username})
    if not found:
        return {"status":0,"message":"Not allowed"}
    
    resp = requests.post("http://nodemgr:8887",json={"port":port}).json()
    if resp["msg"]!="OK":
        return {"status":0,"message":resp["msg"]}
    
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(hostname=resp["ip"],username=resp["username"],password=resp["password"])
    # 2 fetch code artifacts
    
    download_zip(username.lower(),app_name+".zip", True)
    file_path = '../uploads/'+username.lower()+'/'+app_name
    with open(file_path+'/appmeta.json') as f:
        configs = json.load(f)

    with open(file_path+'/controller.json') as f:
        controllers = json.load(f)

    with open(file_path+'/sensor.json') as f:
        sensors = json.load(f)
    
    sensor_list = [s["sensor_instance_type"] for s in sensors["sensor_instance_info"]]
    controller_list = [s["controller_instance_type"] for s in controllers["controller_instance_info"]]
    generate_docker(file_path,{"base":configs["base"],"requirements":configs["lib"],"dependency":configs["dependencies"],"filename":configs["main_file"], "env":configs["env"]},sensor_list,controller_list,username)
    # 3 sensor binding
    # TBD by sensor manager after integration
    for item in sensors["sensor_instance_info"]:
        threading.Thread(target=produce, args=(item["sensor_instance_type"],item["rate"],)).start()

    # 4 build and deploy
    fp = app_name+"_vol_"+str(uuid.uuid1())
    os.mkdir(fp)
    #'" + fp +"'
    ver = "latest" if (configs["version"]=="") else str(configs["version"])
    logger.info('docker build -t '+app_name+':'+ver+' ' +file_path+'/')
    out=os.system('docker build -t '+app_name+':'+ver+' ' + file_path +'/')
    # print("Build result: ",out)
    if out!=0:
        return {"status":0,"message":"Failed build due to invalid configs"}
    if 'admin' in found["role"] or True: 
        container_name = app_name
    else:
        return {"status":0,"message":"Invalid user"}
    
    os.system("docker rm " + container_name)
    
    # out = os.system("docker run -d -v "+fp+":/home --name=" +container_name +' '+app_name)   

    # execute the command and capture its output
    result = subprocess.run("docker network create "+username+"_net", stdout=subprocess.PIPE, shell=True)
    result = subprocess.run("docker run -d --net="+username+"_net -v "+fp+":/home --name=" +container_name +' '+app_name, stdout=subprocess.PIPE, shell=True)
    # decode the output and print it
    output = result.stdout.decode()
    logger.info("Docker run status %s",output)

    # _,stdout,stderr=os.system("docker ps -aqf 'name="+ container_name+"'")
    result = subprocess.run("docker ps -aqf name="+container_name, stdout=subprocess.PIPE, shell=True)
    output = result.stdout.decode()[:-1]
    if "app_runtimes" in db.list_collection_names():
        print("The collection already exists.")
    else:
        # Create the collection
        collection = db.create_collection("app_runtimes")
    collection = db["app_runtimes"]
    mydata = {"node_id": output, "app": app_name, "deployed_by":username, "volume":fp}

    collection.insert_one(mydata)
    return {"status":1,"runtime_id":output,"message":"Deployed successfully"}

def stop_util(app_name,username,type="app_runtimes"):
    found = db['users'].find_one({'username':username})
    if not found:
        return {"status":0,"message":"No such user"}
    app_found = db[type].find_one({'app':app_name, "status": True})
    if not app_found:
        return {"status":0,"message":"No such deployed app found running"}
    elif 'admin' not in found["role"] and app_found["deployed_by"]!=username:
        return {"status":0,"message":"Invalid user"}
    
    query = {"app": app_name, "status": True}    
    results = db[type].find(query)
    for result in results:
        app_name = result.get("app")    
        if app_name:
            res = subprocess.run("hostname -i", stdout=subprocess.PIPE, shell=True)           
            self_ip = res.stdout.decode()[-1]
            if result['machine']['ip'] != self_ip:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=result['machine']["ip"],username=result['machine']["username"],password=result['machine']["password"])
                _,res,_ = ssh.exec_command("docker container stop "+app_name)
                output = res.read().decode()
            else:
                res = subprocess.run("docker container stop "+app_name, stdout=subprocess.PIPE, shell=True)           
                output = res.stdout.decode()
            print("Docker run status ",output)
            db[type].update_one({"_id": result["_id"]}, {"$set": {"status": False}})
            return output
    return "No app found running"
    
def restart_util(app_name,username,type="services"):
    found = db['users'].find_one({'username':username})
    if not found:
        return {"status":0,"message":"No such user"}
    app_found = db[type].find_one({'app':app_name, "status": False})
    if not app_found:
        return {"status":0,"message":"No such deployed app found stopped"}
    elif 'admin' not in found["role"] and app_found["deployed_by"]!=username:
        return {"status":0,"message":"Invalid user"}
    
    query = {"app": app_name, "status": False}    
    results = db[type].find(query)
    for result in results:
        app_name = result.get("app")    
        if app_name:
            res = subprocess.run("hostname -i", stdout=subprocess.PIPE, shell=True)           
            self_ip = res.stdout.decode()[-1]
            if result['machine']['ip'] != self_ip:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=result['machine']["ip"],username=result['machine']["username"],password=result['machine']["password"])
                _,res,_ = ssh.exec_command("docker run -d --net="+app_found["deployed_by"]+"_net -v "+result['volume']+":/home --name="+app_name+" "+app_name)
                output = res.read().decode()[:-1]
            else:
                res = subprocess.run("docker run -d --name="+app_name+" "+app_name, stdout=subprocess.PIPE, shell=True)           
                output = res.stdout.decode()
            print("Docker run status ",output)
            db[type].update_one({"_id": result["_id"]}, {"$set": {"status": False}})
            return output
    return "No app found running"

def get_services(req):
    user = db["users"].find_one({"username":req["username"]})
    if user["role"]=="admin":
        results = db["services"].find()
    elif user["role"]=="app_admin":
        query = {"deployed_by" : req["username"]}    
        results = db["app_runtimes"].find(query)
    else:
        query = {"type" : "open"}
        results = db["services"].find(query)
    app_names = []
    for result in results:        
        app_name = result.get("app")
        if app_name:  
            app_names.append(app_name)
    print(app_names)


if __name__=="__main__":
    print(deploy_util("sample_app","Admin"))
    # print("SSH OUT>>>>>>>>>>>>>", stdout.read().decode())