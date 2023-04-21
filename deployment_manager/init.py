import threading
import json
import os
import uuid
import subprocess
import zipfile
import requests
import argparse

from mockdata import produce, create_topic

parser = argparse.ArgumentParser(description='Sets up deployment')
parser.add_argument('--app_type', type=str, default='app', help='App or service')
parser.add_argument('--kafka_broker', type=str, required=True, help='broker uri')
parser.add_argument('--kafka_rest', type=str, default='192.168.137.51:18082', help='rest api uri')
parser.add_argument('--name', type=str, required=True, help='app or service name')
parser.add_argument('--user', type=str, required=True, help='who is deploying')
parser.add_argument('--port', type=str, default='', help='Port to expose')
args = parser.parse_args()

# import configparser
# config = configparser.ConfigParser()
# config.read('.env')
# configs = config['local']

def generate_docker(fp,service, sensor_topic, controller_topic, username):
    df = open(fp+'/scripts/Dockerfile', 'w')
    
    dependency = service['dependencies']   #other service topics

    for ser in dependency['platform']:
        requests.post("deployment_mgr:8888/deploy",json={"appname":ser,"user":username,"app_type":"service"})
        # pass

    for ser in dependency['bundle']:
        if dependency['bundle'][ser]==True:
            if len(ser.split())>1:
                x = ser[:ser.find(' ')]
                subprocess.run("docker run -d --net="+username+"_net --name "+ser+"_"+username.lower()+" "+x)
            else:
                subprocess.run("docker run -d --net="+username+"_net --name "+ser+"_"+username.lower()+" "+ser)
        else:
            out=os.system('docker build -t '+ser+':latest '+ser+'/')
            # logger.info("Build result: ",out)
            if out!=0:
                print("Some error occured starting your service: "+ser)
                os.remove('Dockerfile')
                return
            subprocess.run("docker run -d --net="+username+"_net --name "+ser+"_"+username.lower()+" "+ser)
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
        for package in service['lib']:
            f.write(package+"\n")
        if "requests" not in service['lib']:
            f.write("requests\n") # for data adapter

    df.write('ADD . ./home\n') # COPY SRC
    df.write('CMD cd home\n')
    df.write('RUN pip3 install --no-cache-dir -r ./home/requirements.txt\n')
    # df.write('EXPOSE '+str(service["port"])+'/tcp\n')

    # keyword_args = (' ').join(dependency)
    runcmd = 'ENTRYPOINT python3 -u /home/' + service['main_file'] + ' ' + (' ').join(sensor_topic) + ' ' + (' ').join(controller_topic) # + " " + keyword_args
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
                # if "location" in sensor and sensor["location"]==[device]:
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
    
def deploy_util(app_name,username):
    # os.chdir("../uploads/"+username)
    flag=False
    for file_name in os.listdir("."):
        if file_name==app_name:
            flag=True
            break
    
    if not flag:
        with zipfile.ZipFile(app_name+".zip") as zip_file:
            zip_file.extractall(".")

    ver = "latest"
    src = ""
    file_path = app_name
    if args.app_type=='app':
        with open(file_path+'/configuration/appmeta.json') as f:
            configs = json.load(f)

        with open(file_path+'/configuration/controller.json') as f:
            controllers = json.load(f)

        with open(file_path+'/configuration/sensor.json') as f:
            sensors = json.load(f)
        
        sensor_list = [s["sensor_instance_type"] for s in sensors["sensor_instance_info"]]
        controller_list = [s["controller_instance_type"] for s in controllers["controller_instance_info"]]
        result = subprocess.run("docker network create "+username+"_net", stdout=subprocess.PIPE, shell=True)
        result = result.stdout.decode()[:-1]
        if "Error" in result and "already exists" not in result:
            return {"status":0,"message":"Failed to create network for deployment"}
        ver = "latest" if (configs["version"]=="") else str(configs["version"])
        src = "/scripts"
    
    if not os.path.exists(file_path+src+"/Dockerfile"):
        generate_docker(file_path,configs,sensor_list,controller_list,username)
        # 3 sensor binding
        # TBD by sensor manager after integration

        device_instance = fetch_n_map_sensors(sensors["sensor_instance_info"],controllers["controller_instance_info"])
        
        # device_instance = {"sensors":{"temperature":[1,2,3],"humidity":[4],"brightness":[5,6]},
        #                    "controllers":{"temperature":[1],"brightness":[6]}}
        print("Got current device ids: ",)
        
        worklist = []
        for item in sensors["sensor_instance_info"]:
            for instance in device_instance["sensors"][item["sensor_instance_type"]]:
                create_topic(instance,args.kafka_broker)
                threading.Thread(target=produce, args=(instance,item["rate"],args.kafka_broker,)).start()
                worklist.append({"type":"sensor","name":item,"device_id":instance})
        
        print("worklist>> ",worklist)
        # build adapter
        check_request(file_path,device_instance,username+"_"+app_name,args.kafka_rest)

        # 4 build and deploy
        print('docker build -t '+app_name+':'+ver+' ' +file_path+src)
        print(subprocess.run("ls "+file_path+src, stdout=subprocess.PIPE, shell=True).stdout.decode()[:-1])

        out=os.system('docker build -t '+app_name+':'+ver+' ' + file_path+src)
        if out!=0:
            return {"status":0,"message":"Failed build due to invalid configs"}
        else:
            print("Build successful")
    
    elif len(subprocess.run("docker images "+app_name, stdout=subprocess.PIPE, shell=True).stdout.decode())<3:
        out=os.system('docker build -t '+app_name+':'+ver+' ' + file_path +src)
        if out!=0:
            return {"status":0,"message":"Failed build due to invalid configs"}
        else:
            print("Build successful")

    if args.app_type=='app':
        container_name = (username+"_"+app_name).lower()
    else:
        container_name = app_name.lower()
    # if args.replica==True:

    if args.app_type=='service' and len(subprocess.run(f'docker  ps --filter "name=^{container_name}$"', stdout=subprocess.PIPE, shell=True).stdout.decode()[:-1].split("\n"))>1:
        return {"status":1,"runtime_id":container_name,"message":"Already deployed"}
    os.system("docker rm " + container_name) # in case already present
    
    # out = os.system("docker run -d -v "+fp+":/home --name=" +container_name +' '+app_name)   
    fp=""
    # execute the command and capture its output
    if args.app_type=='service':
        if args.port!='':
            internal_port = str(5000+int(app_name[3:]))
            result = subprocess.run("docker run -d -p"+args.port+":"+internal_port+" --name=" +container_name+' '+app_name, stdout=subprocess.PIPE, shell=True)
        else:
            result = subprocess.run("docker run -d --net="+username+"_net --name=" +container_name+' '+app_name, stdout=subprocess.PIPE, shell=True)
    else:
        fp = app_name+"_vol_"+str(uuid.uuid1())
        os.mkdir(fp)
        result = subprocess.run("docker run -d -p"+str(configs["port"])+":"+str(configs["port"])+" --net="+username+"_net -v "+fp+":/home --name=" +container_name+' '+app_name+':'+ver, stdout=subprocess.PIPE, shell=True)
    # decode the output and print it
    output = result.stdout.decode()
    print("Docker run status %s",output)

    # _,stdout,stderr=os.system("docker ps -aqf 'name="+ container_name+"'")
    result = subprocess.run("docker ps -aqf name="+container_name, stdout=subprocess.PIPE, shell=True)
    output = result.stdout.decode()[:-1]
    if len(output)>0:
        return {"status":1,"runtime_id":output,"vol":fp,"message":"Deployed successfully"}
    else:
        return {"status":0,"message":""}

print(deploy_util(args.name,args.user),end="")

#### ONE TIME TESTING
# download_zip("ashish","special.zip")

# os.chdir("../uploads/ashish")
# with zipfile.ZipFile("special.zip") as zip_file:
#     zip_file.extractall(".")