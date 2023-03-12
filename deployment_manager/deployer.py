import flask
import threading
import requests
import json
import os
import pymongo
import paramiko
import uuid

client = pymongo.MongoClient("localhost",27017)
db = client['IAS']

def generateDocker(service, sensor_topic, controller_topic):
    df = open('Dockerfile', 'w')
    pip = service['requirements']
    filename = service['filename']
    
    dependency = service['dependency']   #other service topics

    baseimage = '''from base_image\n'''
    df.write(baseimage)
    df.write('\n')

    env = 'RUN pip3 install flask\n'
    df.write(env)

    for package in pip:
        cmd = 'RUN pip3 install ' + package + ' ; exit 0\n'
        df.write(cmd)
    df.write('\n')


    file = 'ADD ' + filename + ' .\n'
    df.write(file)
    df.write('\n')

    dependency_topics = dependency.join(' ')
    df.write('ENTRYPOINT python3 -u ' + filename + ' ' + sensor_topic + ' ' + controller_topic + " " + dependency_topics)
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
        file_path = '../'+req['user']+'/'+req['appname']+'/config.json'
        with open(file_path) as f:
            configs = json.load(f)
        
        generateDocker({"requirements":"numpy","dependency":req["services"],"filename":req["appname"]},configs["sensors"].keys(),configs["controllers"])
        # 3 sensor binding
        config

        # 4 build and deploy
        os.mkdir("runtime_"+uuid.uuid1())
        
        

 
        image_name = servicename
        print('echo root | sudo -S docker build -t ' + image_name + " '" + serviceid +"'")
        stdin,stdout,stderr=os.system('echo root | sudo -S docker build -t ' + image_name + " '" + serviceid +"'")
        checkforError(stdout,stderr)
        print(stderr.readlines())
        if username == 'admin': 
            container_name = servicename
        else:
            container_name= serviceid
        stdin,stdout,stderr=os.system("echo root | sudo -S docker rm " + container_name)
        checkforError(stdout,stderr)
        stdin,stdout,stderr=os.system("echo root | sudo -S docker run -d --network='host' -v ${HOME}:/home --name=" +container_name +' '+image_name)
        checkforError(stdout,stderr)
        # print(stdout.readlines())
        stdin,stdout,stderr=os.system("echo root | sudo -S docker ps -aqf 'name="+ container_name+"'")
        print("Contaier id is ")
        lines = stdout.readlines()
        conid = lines[0]
        print(conid)
        return flask.jsonify({"status":"ok","runtime_id":conid})

    app.run(host = '0.0.0.0',port = 8888)
	

if __name__ == '__main__':
    app = flask.Flask('deploymgr')
    req_handler(app)
    # while True:
        # threading.Thread(target=req_handler,args=(app,)).start()
        # t1.join()
	