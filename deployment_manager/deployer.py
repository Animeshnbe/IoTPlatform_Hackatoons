import flask
import threading
import requests
import json
import pymongo

client = pymongo.MongoClient("localhost",27017)
db = client['IAS']

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
        # 3 sensor binding

        
        return flask.jsonify({"status":"ok"})

    app.run(host = '0.0.0.0',port = 8888)
	

if __name__ == '__main__':
    app = flask.Flask('deploymgr')
    req_handler(app)
    # while True:
        # threading.Thread(target=req_handler,args=(app,)).start()
        # t1.join()
	