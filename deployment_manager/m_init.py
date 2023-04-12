import threading
import json
import os
import sys
import uuid
import subprocess
import zipfile
import requests

from mockdata import produce

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

def check_request(worklist, consumer_group, base_uri, name="test"):  
  # get_all_sensors()

    res = requests.get("{base_uri}/topics").json()
    for item in worklist["sensor"].values():
        for topic in item:
            if topic not in res:
                return 0
            
  with open("data_adapter.py","w") as f:
    f.write(f'''

# 
# pretty(res)

def attach_sensors(names):
  for name in names:
    # Register consumer
    res = requests.post(
        url="{base_uri}/consumers/{consumer_group}",
        data=json.dumps({
            "name": name,
            "format": "json",
            "auto.offset.reset": "earliest",
            "auto.commit.enable": "false",
            "fetch.min.bytes": "1",
            "consumer.request.timeout.ms": "10000"
        }),
        headers={"Content-Type": "application/vnd.kafka.v2+json"}).json()
    print(res)

    # Subscribe
    res = requests.post(
        url="{base_uri}/consumers/test_group/instances/"+name+"/subscription",
        data=json.dumps({"topics": {consume}}),
        headers={"Content-Type": "application/vnd.kafka.v2+json"})

    # Consume
    while True:
        res = requests.get(
            url=f"{base_uri}/consumers/test_group/instances/test_consumer2/records",
            params={"timeout":1000,"max_bytes":100000,"partition":0,"offset":1,},
            headers={"Accept": "application/vnd.kafka.json.v2+json"}).json()
        if res:
            return res

# # Commit
# res = requests.post(
#     url=f"{base_uri}/consumers/test_group/instances/test_consumer/offsets",
#     data=json.dumps(
#         dict(partitions=[
#             dict(topic="test_topic", partition=p, offset=0) for p in [0, 1, 2]
#         ])),
#     headers={"Content-Type": "application/vnd.kafka.v2+json"})

# delete consumer
# res = requests.delete(
#     url=f"{base_uri}/consumers/test_group/instances/test_consumer",
#     headers={"Content-Type": "application/vnd.kafka.v2+json"})

# print(res.json())
''')
    
def deploy_util(app_name,username,kafka):
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

    # device_instance = get_actual_ids(sensor_list,controller_list)
    device_instance = {"sensor":{"temperature":[1,2,3],"humidity":[4],"brightness":[5,6]},
                       "controller":{"temperature":[1],"brightness":[6]}}
    
    # worklist = []
    for item in sensors["sensor_instance_info"]:
        for instance in device_instance["sensor"][item["sensor_instance_type"]]:
            threading.Thread(target=produce, args=(instance,item["rate"],)).start()
            # worklist.append({"type":"sensor","name":item,"device_id":instance})
    
    # build adapter
    check_request(device_instance,username+"_"+app_name,kafka)

    # 4 build and deploy
    fp = app_name+"_vol_"+str(uuid.uuid1())
    os.mkdir(fp)
    #'" + fp +"'
    ver = "latest" if (configs["version"]=="") else str(configs["version"])
    # logger.info('docker build -t '+app_name+':'+ver+' ' +file_path+'/')
    out=os.system('docker build -t '+app_name+':'+ver+' ' + file_path +'/')
    # print("Build result: ",out)
    if out!=0:
        return {"status":0,"message":"Failed build due to invalid configs"}
    
    container_name = app_name
    os.system("docker rm " + container_name) # in case already present
    
    # out = os.system("docker run -d -v "+fp+":/home --name=" +container_name +' '+app_name)   

    # execute the command and capture its output
    result = subprocess.run("docker network create "+username+"_net", stdout=subprocess.PIPE, shell=True)
    result = subprocess.run("docker run -d --net="+username+"_net -v "+fp+":/home --name=" +container_name +' '+app_name, stdout=subprocess.PIPE, shell=True)
    # decode the output and print it
    output = result.stdout.decode()
    # print("Docker run status %s",output)

    # _,stdout,stderr=os.system("docker ps -aqf 'name="+ container_name+"'")
    result = subprocess.run("docker ps -aqf name="+container_name, stdout=subprocess.PIPE, shell=True)
    output = result.stdout.decode()[:-1]
    return {"status":1,"runtime_id":output,"message":"Deployed successfully"}

print(deploy_util(sys.argv[1],sys.argv[2],sys.argv[3]),end="")

#### ONE TIME TESTING
# download_zip("ashish","special.zip")

# os.chdir("../uploads/ashish")
# with zipfile.ZipFile("special.zip") as zip_file:
#     zip_file.extractall(".")