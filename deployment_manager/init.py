import threading
import json
import os
import sys
import uuid
import subprocess
import zipfile
import requests

from mockdata import produce, create_topic

# import configparser
# config = configparser.ConfigParser()
# config.read('.env')
# configs = config['local']

def generate_docker(fp,service, sensor_topic, controller_topic, username):
    df = open(fp+'/scripts/Dockerfile', 'w')
    pip = service['requirements']
    filename = service['filename']
    
    dependency = service['dependency']   #other service topics

    for ser in dependency['platform']:
        deploy_util(ser,username,)
        # pass

    for ser in dependency['bundle']:
        if dependency['bundle'][ser]==True:
            if len(ser.split())>1:
                x = ser[:ser.find(' ')]
                subprocess.run("docker run -d --net="+username+"_net --name "+ser+" "+x)
            else:
                subprocess.run("docker run -d --net="+username+"_net --name "+ser+" "+ser)
        else:
            out=os.system('docker build -t '+ser+':latest '+ser+'/')
            # logger.info("Build result: ",out)
            if out!=0:
                print("Some error occured starting your service: "+ser)
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
        df.write("ENV "+k+"="+str(v)+'\n')
    
    with open(fp+'/scripts/requirements.txt', 'w') as f:
        for package in pip:
            f.write(package+"\n")


    df.write('ADD . ./home\n') # COPY SRC
    df.write('CMD cd home\n')
    df.write('RUN pip3 install --no-cache-dir -r ./home/requirements.txt\n')


    # keyword_args = (' ').join(dependency)
    runcmd = 'ENTRYPOINT python3 -u /home/' + filename + ' ' + (' ').join(sensor_topic) + ' ' + (' ').join(controller_topic) # + " " + keyword_args
    df.write(runcmd.rstrip())
    df.close()

def fetch_n_map_sensors(sensors,controllers):
    # devices = requests.get("http://192.168.137.51:8890/").json()
    with open("dummy.json", "r") as f:
        devices = json.load(f)

    ans = {"sensors":{},"controllers":{}}
    # print(sensors)
    # print([d["sensortype"] for d in devices])
    for sensor in sensors:
        ans["sensors"][sensor["sensor_instance_type"]] = []
        for device in devices:
            if device["sensortype"]==sensor["sensor_instance_type"]:
                ans["sensors"][sensor["sensor_instance_type"]].append(device["id"])
            
                # print(sensor["sensor_instance_type"]," LEFT = ",sensor["sensor_instance_count"])
                if sensor["sensor_instance_count"]>0:
                    sensor["sensor_instance_count"]-=1
                    if sensor["sensor_instance_count"]==0:
                        break


    for sensor in controllers:
        ans["controllers"][sensor["controller_instance_type"]] = []
        for device in devices:
            if device["sensortype"]==sensor["controller_instance_type"]:
                ans["controllers"][sensor["controller_instance_type"]].append(device["id"])
            if sensor["controller_instance_count"]>0:
                sensor["controller_instance_count"]-=1
                if sensor["controller_instance_count"]==0:
                    break

    return ans

def check_request(fp, worklist, consumer_group, base_uri, name="test"):  
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ",worklist)
    res = requests.get(f"http://{base_uri}/topics").json()

    # print(base_uri, res)
    for topiclist in worklist["sensors"].values():
        for topic in topiclist:
            if str(topic) not in res:
                return 0
            
    print("work===========", str(worklist))
    with open(fp+"/scripts/data_adapter.py","w") as f:
        f.write(f'''
import requests
import json
        
devices = {str(worklist)}
def attach_sensors(names):
    # Register consumer
    res = requests.post(
        url="http://{base_uri}/consumers/{consumer_group}",
        data=json.dumps({{
            "name": "{name}",
            "format": "json",
            "auto.offset.reset": "earliest",
            "auto.commit.enable": "false",
            "fetch.min.bytes": "1",
            "consumer.request.timeout.ms": "10000"
        }}),
        headers={{"Content-Type": "application/vnd.kafka.v2+json"}}).json()
    print(res)

    # Subscribe
    topics_raw = []
    for name in names:
        topics_raw.extend(devices["sensors"][name])

    topics = [str(t) for t in topics_raw]
    res = requests.post(
        url="http://{base_uri}/consumers/{consumer_group}/instances/{name}/subscription",
        data=json.dumps({{"topics": topics}}),
        headers={{"Content-Type": "application/vnd.kafka.v2+json"}})

    # Consume
    while True:
        res = requests.get(
            url="http://{base_uri}/consumers/{consumer_group}/instances/{name}/records",
            params={{"timeout":1000,"max_bytes":100000,"partition":0,"offset":1,}},
            headers={{"Accept": "application/vnd.kafka.json.v2+json"}}).json()
        if res:
            # print(res)
            yield res

def send_controller(controller_name,action,instance=None):
    if instance==None:
        for dev in devices["controllers"][controller_name]:
            requests.post("http://action_manager:9825/actionManagerAPI", json={{"user_id":{consumer_group.split('_')[0]},"new_value":action,"device_id":dev}})
    else:
        requests.post("http://action_manager:9825/actionManagerAPI", json={{"user_id":{consumer_group.split('_')[0]},"new_value":action,"device_id":devices["controller"][controller_name][instance]}})

        ''')
    
def deploy_util(app_name,username,kafka):
    # os.chdir("../uploads/"+username)
    with zipfile.ZipFile(app_name+".zip") as zip_file:
        zip_file.extractall(".")

    file_path = app_name
    with open(file_path+'/configuration/appmeta.json') as f:
        configs = json.load(f)

    with open(file_path+'/configuration/controller.json') as f:
        controllers = json.load(f)

    with open(file_path+'/configuration/sensor.json') as f:
        sensors = json.load(f)
    
    sensor_list = [s["sensor_instance_type"] for s in sensors["sensor_instance_info"]]
    controller_list = [s["controller_instance_type"] for s in controllers["controller_instance_info"]]
    result = subprocess.run("docker network create "+username+"_net", stdout=subprocess.PIPE, shell=True)
    generate_docker(file_path,{"base":configs["base"],"requirements":configs["lib"],"dependency":configs["dependencies"],"filename":configs["main_file"], "env":configs["env"]},sensor_list,controller_list,username)
    # 3 sensor binding
    # TBD by sensor manager after integration

    device_instance = fetch_n_map_sensors(sensors["sensor_instance_info"],controllers["controller_instance_info"])
    
    # device_instance = {"sensors":{"temperature":[1,2,3],"humidity":[4],"brightness":[5,6]},
    #                    "controllers":{"temperature":[1],"brightness":[6]}}
    print("Got current device ids: ",)
    
    # worklist = []
    for item in sensors["sensor_instance_info"]:
        for instance in device_instance["sensors"][item["sensor_instance_type"]]:
            create_topic(instance)
            threading.Thread(target=produce, args=(instance,item["rate"],)).start()
            # worklist.append({"type":"sensor","name":item,"device_id":instance})
    
    # build adapter
    check_request(file_path,device_instance,username+"_"+app_name,kafka)

    # 4 build and deploy
    fp = app_name+"_vol_"+str(uuid.uuid1())
    os.mkdir(fp)
    #'" + fp +"'
    ver = "latest" if (configs["version"]=="") else str(configs["version"])
    # logger.info('docker build -t '+app_name+':'+ver+' ' +file_path+'/')
    out=os.system('docker build -t '+app_name+':'+ver+' ' + file_path +'/scripts')
    # print("Build result: ",out)
    if out!=0:
        return {"status":0,"message":"Failed build due to invalid configs"}
    
    container_name = app_name
    os.system("docker rm " + container_name) # in case already present
    
    # out = os.system("docker run -d -v "+fp+":/home --name=" +container_name +' '+app_name)   

    # execute the command and capture its output
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