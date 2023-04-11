import flask
import threading
from utils import deploy_util, stop_util, restart_util, get_services
from heartBeat import heart_beat

def req_handler(app):
    @app.route('/deploy', methods=['POST'])
    def deploy():
        # print(flask.request.get_json())
        req = flask.request.get_json()
        output = deploy_util(req['user'],req['appname'])
        return flask.jsonify(output)

    @app.route('/start_service', methods=['POST'])
    def start():
        req = flask.request.get_json()
        print("Json ",req)
        if req["type"]=='system':
            pass
            # provision docker swarm
            # init node
            # fetch config
        else:
            deploy_util(req['username'],req['service_name'],req['port'])

    @app.route('/stop_service', methods=['POST'])
    def stop():
        req = flask.request.get_json()
        print("Json ",req)
        stop_util(req['username'],req['service_name'], req['type'])

    @app.route('/restart_service', methods=['POST'])
    def restart():
        req = flask.request.get_json()
        print("Json ",req)
        restart_util(req['username'],req['service_name'], req['type'])

    @app.route('/get_services', methods=['GET'])
    def get():
        req = flask.request.get_json()
        print("Json ",req)

        get_services(req)

    @app.route('/test', methods=['POST'])
    def test():
        print("Json ",flask.request.get_json())
        return flask.jsonify({"status":"ok","runtime_id":0})
    app.run(host = '0.0.0.0',port = 8888, threaded=True)
	


if __name__ == '__main__':
    app = flask.Flask('deploymgr')
    t = threading.Thread(target=heart_beat, args=("deployment_manager",))
    t.daemon = True
    t.start()
    req_handler(app)

	