import flask
import threading
import requests
import json
import os
import io
import pymongo
import paramiko
import uuid
import subprocess
from azure.storage.blob import BlobServiceClient
import zipfile

import configparser
config = configparser.ConfigParser()
config.read('.env')
configs = config['local']

from mockdata import produce

import pymongo
client = pymongo.MongoClient(configs["MONGO_URI"],configs["MONGO_PORT"])
db = client['IAS']

def download_zip(container, zip_file_name):
    # print("ARGS +++++ ",container,zip_file_name)
    connect_str = "DefaultEndpointsProtocol=https;AccountName=aman0ias;AccountKey=ejuMHDXoYsp4ktNpndJTqrC0QXgEi7DCv0cJiK94R6ZhMYZa+VmKnYcTNv3T6qIc/qoYnnZbGZPg+AStGotFJA==;EndpointSuffix=core.windows.net"

    container_name = container         #container name
    blob_name = zip_file_name          #zip file name

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    blob_data = io.BytesIO()
    blob_client.download_blob().download_to_stream(blob_data)

    with zipfile.ZipFile(blob_data) as zip_file:
        zip_file.extractall("../"+container)

def generate_docker(fp,service, sensor_topic, controller_topic):
    df = open(fp+'/Dockerfile', 'w')
    pip = service['requirements']
    filename = service['filename']
    
    dependency = service['dependency']   #other service topics

    baseimage = 'FROM '+service["base"]+'\n'
    df.write(baseimage)
    df.write('\n')

    env = 'RUN apt-get update && apt-get install -y python3 python3-pip\n\
RUN pip3 install Flask\n'
    df.write(env)

    for package in pip:
        cmd = 'RUN pip3 install ' + package + ' ; exit 0\n'
        df.write(cmd)
    df.write('\n')


    file = 'ADD ' + filename + ' .\n'
    df.write(file)
    df.write('\n')

    dependency_topics = (' ').join(dependency)
    runcmd = 'ENTRYPOINT python3 -u ' + filename + ' ' + (' ').join(sensor_topic) + ' ' + (' ').join(controller_topic) + " " + dependency_topics
    df.write(runcmd.rstrip())
    df.close()

def deploy_util(app_name,username):
    # 1 verify user
    found = db['users'].find_one({'username':username})
    if not found:
        return {"status":0,"message":"Not allowed"}
    # 2 fetch code artifacts
    # download_zip(username.lower(),app_name+".zip")
    file_path = '../'+username.lower()+'/'+app_name
    with open(file_path+'/appmeta.json') as f:
        configs = json.load(f)

    with open(file_path+'/controller.json') as f:
        controllers = json.load(f)

    with open(file_path+'/sensor.json') as f:
        sensors = json.load(f)
    
    generate_docker(file_path,{"base":configs["base"],"requirements":configs["lib"],"dependency":req["services"],"filename":configs["filename"]},sensors.keys(),configs["controllers"])
    # 3 sensor binding
    # TBD by sensor manager after integration
    for k,v in configs["sensors"].items():
        threading.Thread(target=produce, args=(k,v,)).start()

    # 4 build and deploy
    fp = app_name+"_vol_"+str(uuid.uuid1())
    os.mkdir(fp)
    #'" + fp +"'
    print('docker build -t '+app_name+':latest ' + file_path +'/')
    out=os.system('docker build -t '+app_name+':latest ' + file_path +'/')
    # print("Build result: ",out)
    if out!=0:
        return flask.jsonify({"status":0,"message":"Failed build due to invalid configs"})
    if found["usertype"] == 'admin': 
        container_name = app_name
    else:
        return flask.jsonify({"status":0,"message":"Invalid user"})
    
    os.system("docker rm " + container_name)
    
    # out = os.system("docker run -d -v "+fp+":/home --name=" +container_name +' '+app_name)   

    # execute the command and capture its output
    # result = subprocess.run("docker run -d -v runtime_special:/home --name=special special", stdout=subprocess.PIPE, shell=True)
    result = subprocess.run("docker run -d --net="+username+"_net -v "+fp+":/home --name=" +container_name +' '+app_name, stdout=subprocess.PIPE, shell=True)
    # decode the output and print it
    output = result.stdout.decode()
    print("Docker run status ",output)

    # _,stdout,stderr=os.system("docker ps -aqf 'name="+ container_name+"'")
    result = subprocess.run("docker ps -aqf name="+container_name, stdout=subprocess.PIPE, shell=True)
    output = result.stdout.decode()
    if "runtime" in db.list_collection_names():
        print("The collection already exists.")
    else:
        # Create the collection
        collection = db.create_collection("runtime")
    collection = db["runtime"]
    mydata = {"node_id": output, "app": app_name, "deployed_by":username}

    collection.insert_one(mydata)
    return {"status":1,"runtime_id":output,"message":"Deployed successfully"}

def stop_util(app_name,username):
    # db.
    result = subprocess.run("docker container stop "+app_name, stdout=subprocess.PIPE, shell=True)
    # decode the output and print it
    output = result.stdout.decode()
    print("Docker run status ",output)
    return output

def get_services(username):


def test():
    print("hello")