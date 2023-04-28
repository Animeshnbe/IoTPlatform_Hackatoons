import os
import yaml
import pymongo
import flask
import json
import shutil               #to move file
import paramiko
import subprocess
from os.path import join, dirname
from dotenv import load_dotenv
import jwt
from functools import wraps

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def create_flow(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    parent_dict = {}
    for d in data:
        if d["type"] == "tab":
            parent_dict[d["id"]] = []
        elif d["type"] == "comment" :
            continue
        elif d["z"] in parent_dict :
            parent_dict[d["z"]].append(d)

    
    ordered_dict = {}
    
    for lst in parent_dict.values() :
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

        ordered_dict[ordered[0]["id"]] = ordered
        
    # print(json.dumps(ordered_dict))
    return ordered_dict

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
    def test1():
        return 'Hello World'
    
    @app.route('/accept_workflow', methods=['POST', 'GET'])
    @authorized
    def test():
        # print("Json ",flask.request.get_json())
        req = flask.request.get_json()
        # print(db["app_runtimes"].find_one({"app":"flasker"}))
        try:
            ordered_dict = create_flow("../flows/flows.json")
            print(ordered_dict)
            
            for id,flow in ordered_dict.items():
                services = {}
                flag = False
                # apps = []
                for item in flow:
                    if item["type"]=="http request":
                        flag = True
                        app_name = item["name"]
                        port = get_service_port(app_name)
                        services[app_name] = {
                            'build': {
                                'context': f'../../services/{app_name}',
                            },
                            'ports':[
                                port+":"+port
                            ],
                            'networks':[
                                'network'+id
                            ]
                        }
                        # apps.append(app_name)

                if flag:
                    networks = {
                        'network'+id: {
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

                    os.mkdir("../flows/flow_"+id)
                    # put the compose file here
                    shutil.move("docker-compose.yml", "../flows/flow_"+id)
                    # run the compose command
                    # ssh = paramiko.SSHClient()
                    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    # ssh.connect(hostname=os.getenv("NODE_RED_IP"),username=os.getenv("username"),password=os.getenv("password"))
                    # ##### CHANGE AS RE
                    # ssh.exec_command("cd ../flows/flow_"+id)
                    # _,res,_ = ssh.exec_command("docker compose up")
                    # ssh.close()
                    os.chdir("../flows/flow_"+id)
                    res = subprocess.run("docker compose up", stdout=subprocess.PIPE, shell=True)           
                    output = res.stdout.decode()[-1]
                    # output = res.read().decode()
                    if 'Error' not in output:
                        db['workflows'].insert_one({"id":output,"username":req['username']})
                    print(output)
                    break

            return flask.jsonify({"status":1})
        except Exception as ex:
            print(ex)
            return flask.jsonify({"status":0, "message":"Could not start services in your workflow"})
    
    app.run(host = '0.0.0.0',port = 8886, threaded=True)


