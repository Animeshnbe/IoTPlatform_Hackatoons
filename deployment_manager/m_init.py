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
from loggingUtility import logger_func
from mockdata import produce

logger = logger_func()

import configparser
config = configparser.ConfigParser()
config.read('.env')
configs = config['local']

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
    os.chdir("../uploads/"+username)
    with zipfile.ZipFile(app_name+".zip") as zip_file:
        zip_file.extractall(".")

    file_path = app_name
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
    if username == '__admin' or True: 
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


# download_zip("ashish","special.zip")

os.chdir("../uploads/ashish")
with zipfile.ZipFile("special.zip") as zip_file:
    zip_file.extractall(".")