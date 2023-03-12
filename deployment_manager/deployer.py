import flask
import threading
import requests
import json
import os
import pymongo
import paramiko
import uuid
from azure.storage.blob import BlobServiceClient
import zipfile
import io

from mockdata import produce

client = pymongo.MongoClient("localhost",27017)
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
        for file_name in zip_file.namelist() :
            zip_file.extract(file_name)

def generate_docker(fp,service, sensor_topic, controller_topic):
    df = open(fp+'/Dockerfile', 'w')
    pip = service['requirements']
    filename = service['filename']
    
    dependency = service['dependency']   #other service topics

    baseimage = 'FROM '+service["base"]+'\n'
    df.write(baseimage)
    df.write('\n')

    env = 'RUN apt-get update && apt-get install -y python3 python3-pip\n\
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
    runcmd = 'ENTRYPOINT python3 -u ' + filename + ' ' + (' ').join(sensor_topic) + ' ' + (' ').join(controller_topic) + " " + dependency_topics
    df.write(runcmd.rstrip())
    df.close()

def req_handler(app):
    @app.route('/deploy', methods=['POST'])
    def deploy():
        # print(flask.request.get_json())
        req = flask.request.get_json()

        # 1 verify user
        found = db['users'].find_one({'username':req['user']})
        if not found:
            return flask.jsonify({"status":"bhag bsdk"})
        # 2 fetch code artifacts
        download_zip(req['user'].lower(),req['appname']+".zip")
        file_path = '../'+req['user']+'/'+req['appname']
        with open(file_path+'/config.json') as f:
            configs = json.load(f)
        
        generate_docker(file_path,{"base":configs["env"],"requirements":configs["requirements"],"dependency":req["services"],"filename":configs["filename"]},configs["sensors"].keys(),configs["controllers"])
        # 3 sensor binding
        # TBD by sensor manager after integration
        for k,v in configs["sensors"].items():
            threading.Thread(target=produce, args=(k,v,)).start()

        # 4 build and deploy
        fp = "runtime_"+req["appname"]+"_"+str(uuid.uuid1())
        os.mkdir(fp)
        #'" + fp +"'
        # print('docker build -t '+req["appname"]+':latest ' + file_path +'/')
        # out=os.system('docker build -t '+req["appname"]+':latest ' + file_path +'/')
        # # print("Build result: ",out)
        # if out!=0:
        #     return flask.jsonify({"status":"failed build due to invalid configs"})
        if found["usertype"] == 'admin': 
            container_name = req["appname"]
        else:
            return flask.jsonify({"status":"Invalid user"})
        # print("docker run -d --network='host' -v ${HOME}:/home --name="+container_name+" "+req["appname"])
        os.system("docker rm " + container_name)
        
        out = os.system("docker run -d -v "+fp+":/home --name=" +container_name +' '+req["appname"])
        print(out)

        # # # print(stdout.readlines())
        # _,stdout,stderr=os.system("docker ps -aqf 'name="+ container_name+"'")
        # lines = stdout.readlines()
        # conid = lines[0]
        # print("Container id",conid)
        return flask.jsonify({"status":"ok","runtime_id":0})

    app.run(host = '0.0.0.0',port = 8888, threaded=True)
	


if __name__ == '__main__':
    app = flask.Flask('deploymgr')
    req_handler(app)
    @app.route('/test', methods=['POST'])
    def test():
        print(flask.request.get_json())
        return flask.jsonify({"status":"ok","runtime_id":0})
    # while True:
        # threading.Thread(target=req_handler,args=(app,)).start()
        # t1.join()
	