import flask
import threading
import requests
import json
import os
import pymongo
import paramiko
import uuid
from mockdata import produce

client = pymongo.MongoClient("localhost",27017)
db = client['IAS']

def generateDocker(fp,service, sensor_topic, controller_topic):
    df = open(fp+'/Dockerfile', 'w')
    pip = service['requirements']
    filename = service['filename']
    
    dependency = service['dependency']   #other service topics

    baseimage = 'FROM '+service["base"]+'\n'
    df.write(baseimage)
    df.write('\n')

    env = 'RUN apt-get update && apt-get install -y python3 python3-pip\n \
            RUN pip3 install flask\n'
    df.write(env)

    for package in pip:
        cmd = 'RUN pip3 install ' + package + ' ; exit 0\n'
        df.write(cmd)
    df.write('\n')


    file = 'ADD ' + filename + ' .\n'
    df.write(file)
    df.write('\n')

    dependency_topics = (' ').join(dependency)
    df.write('ENTRYPOINT python3 -u ' + filename + ' ' + (' ').join(sensor_topic) + ' ' + (' ').join(controller_topic) + " " + dependency_topics)
    df.close()

def req_handler(app):
    @app.route('/deploy', methods=['POST'])
    def deploy():
        # print(flask.request.get_json())
        req = flask.request.get_json()

        # 1 verify user
        found = db['users'].find({'username':req['user']})
        if not found:
            return flask.jsonify({"status":"bhag bsdk"})
        # 2 fetch code artifacts
        file_path = '../'+req['user']+'/'+req['appname']
        with open(file_path+'/config.json') as f:
            configs = json.load(f)
        
        generateDocker(file_path,{"base":configs["env"],"requirements":configs["requirements"],"dependency":req["services"],"filename":configs["filename"]},configs["sensors"].keys(),configs["controllers"])
        # 3 sensor binding
        # TBD by sensor manager after integration
        for k,v in configs["sensors"].items():
            threading.Thread(target=produce, args=(k,v,)).start()

        # 4 build and deploy
        # fp = "runtime_"+req["appname"]+"_"+str(uuid.uuid1())
        # os.mkdir(fp)
        #'" + fp +"'
        print('docker build -t ' + req["appname"] + " .")
        _,stdout,stderr=os.system('docker build -t ' + req["appname"] + " '" + file_path +"'")
        lines = stdout.readlines()
        if len(lines) != 0:
            print(lines[0])
        lines = stderr.readlines()
        if len(lines) != 0:
            print("Error")
            print(lines[0])
        if found.usertype == 'admin': 
            container_name = req["appname"]
        else:
            return flask.jsonify({"status":"GO AWAY"})
        print("docker run -d --network='host' -v ${HOME}:/home --name="+container_name+" "+req["appname"])
        # _,stdout,stderr=os.system("docker rm " + container_name)
        
        # _,stdout,stderr=os.system("docker run -d --network='host' -v ${HOME}:/home --name=" +container_name +' '+req["appname"])

        # # # print(stdout.readlines())
        # _,stdout,stderr=os.system("docker ps -aqf 'name="+ container_name+"'")
        # lines = stdout.readlines()
        # conid = lines[0]
        # print("Container id",conid)
        return flask.jsonify({"status":"ok","runtime_id":0})

    app.run(host = '0.0.0.0',port = 8888)
	

if __name__ == '__main__':
    app = flask.Flask('deploymgr')
    req_handler(app)
    # while True:
        # threading.Thread(target=req_handler,args=(app,)).start()
        # t1.join()
	