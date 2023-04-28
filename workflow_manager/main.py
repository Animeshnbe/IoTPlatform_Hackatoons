import os
import yaml
import pymongo
import flask
import json
# import shutil               #to move file
import paramiko
# import subprocess
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from functools import wraps

dotenv_path = join(dirname(__file__), '.env')
load_dotenv()

def create_flow(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    parent_dict = {}
    flows = {}
    for d in data:
        if d["type"] == "tab":
            parent_dict[d["id"]] = []
            flows[d["id"]] = d["label"]
        elif d["type"] == "comment" :
            continue
        elif d["z"] in parent_dict :
            parent_dict[d["z"]].append(d)

    
    ordered_dict = {}
    
    for key,lst in parent_dict.items() :
        ids = set()
        dict_key = {}
        for d in lst :
            ids.add(d["id"])
            dict_key[d["id"]] = d

        for d in lst :
            for item in d["wires"] :
                for i in item :
                    ids.remove(i)

        head = None           
        for i in ids :
            head = i

        if head == None :
            continue 

        ordered = [dict_key[head]]

        i = 0

        while i != len(lst) - 1 :
            for item in ordered[i]["wires"] :
                for j in item :
                    ordered.append(dict_key[j])

            i += 1

        ordered_dict[key] = ordered
        
    # print(json.dumps(ordered_dict))
    return ordered_dict, flows

def get_service_port(service_name):
    all_ports = {
        "app1":"5001",
        "app2":"5002",
        "app3":"5003",
        "app4":"5004",
        "app5":"5005"
    }
    return all_ports[service_name]

app = flask.Flask('workflow')
app.config['SECRET_KEY'] = 'mysecretkey'

def authorized(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = flask.request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return flask.jsonify({'error': 'Missing token'}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return flask.jsonify({'error': 'Invalid token'}), 401
        name = payload['name']
        if name not in ['ui','app_manager','monitoring']:
            return flask.jsonify({'error': 'Unauthorized'}), 401
        flask.request.user = name
        return f(*args, **kwargs)
    return decorated

if __name__ == '__main__':
    client = pymongo.MongoClient(os.getenv("MONGO_DB"))
    db = client['IAS_Global']

    @app.route('/test', methods=['POST', 'GET'])
    @authorized
    def test():
        return 'Hello World'
    
    @app.route('/accept_workflow', methods=['POST', 'GET'])
    @authorized
    def start():
        # print("Json ",flask.request.get_json())
        req = flask.request.get_json()
        # print(db["app_runtimes"].find_one({"app":"flasker"}))
        try:
            ordered_dict, flow_labels = create_flow("../flows/flows.json")
            # print(ordered_dict)
            
            for id,flow in ordered_dict.items():
                services = {}
                flag = False
                # apps = []
                zips = []
                for item in flow:
                    if item["type"]=="http request":
                        flag = True
                        app_name = item["name"]
                        port = get_service_port(app_name)
                        zips.append(app_name+".zip")
                        services[app_name] = {
                            'build': {
                                'context': app_name,
                            },
                            'ports':[
                                port+":"+port
                            ],
                            'networks':[
                                'network_'+id
                            ]
                        }
                        # apps.append(app_name)

                if flag:
                    networks = {
                        'network_'+id: {
                                    'driver': 'bridge'
                                }
                    }

                    compose_data = {
                        'version': '3',
                        'services': services,
                        'networks': networks,
                    }

                    with open('docker-compose.yml', 'w') as f:
                        yaml.dump(compose_data, f, sort_keys=False)

                    # os.mkdir("../flows/flow_"+id)
                    # put the compose file here
                    # shutil.move("docker-compose.yml", "../flows/flow_"+id)
                    # run the compose command
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(hostname=os.getenv("NODE_RED_IP"),username=os.getenv("user"),password=os.getenv("password"))
                    ##### CHANGE AS RE
                    c_name = req['username']+"_"+id[:5]
                    ssh.exec_command("mkdir -p flows/"+c_name)
                    ftp_client=ssh.open_sftp()
                    ftp_client.chdir("flows/"+c_name)
                    ftp_client.put("docker-compose.yml","docker-compose.yml")
                    for zf in zips:
                        ftp_client.put("../services/"+zf,zf)
                        _,res,_ = ssh.exec_command("unzip -d flows/"+c_name+" flows/"+c_name+"/"+zf+" && rm flows/"+c_name+"/"+zf)
                        # print(res.read().decode())
                    ftp_client.close()
                    _,stdout,stderr = ssh.exec_command("docker compose -f flows/"+c_name+"/docker-compose.yml up -d")
                    # os.chdir("../flows/flow_"+id)
                    # res = subprocess.run("docker compose up", stdout=subprocess.PIPE, shell=True)           
                    # output = res.stdout.decode()[-1]
                    print(stdout.channel.recv_exit_status())
                    output = stdout.read().decode()
                    errors = stderr.read().decode().strip()
                    # print("After docker compose", output)
                    # print("Output ",errors)
                    ssh.close()
                    if len(errors)>0 and errors.count('Started')==len(zips):
                        # print("inserting... ")
                        db['workflows'].insert_one({"flowid":id,"name":flow_labels[id],"node_id":c_name,"username":req['username']})
                    # print("Ins after ",output)
                    # break

            return flask.jsonify({"status":1})
        except Exception as ex:
            print("Exception ",ex)
            return flask.jsonify({"status":0, "message":"Could not start services in your workflow"})
    
    @app.route('/stop_workflow', methods=['POST', 'GET'])
    @authorized
    def stop():
        # print("Json ",flask.request.get_json())
        req = flask.request.get_json()
        # print(db["app_runtimes"].find_one({"app":"flasker"}))
        try:
            x = db["workflows"].find_one({"flowid":req["id"]})
            if x is not None:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=os.getenv("NODE_RED_IP"),username=os.getenv("user"),password=os.getenv("password"))
                _,_,stderr = ssh.exec_command("docker compose -f flows/"+x['node_id']+"/docker-compose.yml down")
                errors = stderr.read().decode().strip()
                if len(errors)>0:
                    db["workflows"].delete_one({"_id": x["_id"]})
            return flask.jsonify({"status":1})
        except Exception as ex:
            print(ex)
            return flask.jsonify({"status":0, "message":"Could not stop your workflow"})
    app.run(host = '0.0.0.0',port = 8886, threaded=True)


