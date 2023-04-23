import flask
import threading
from utils import scheduler_consumer, deploy_util, stop_util, restart_util, get_services
from heartBeat import heart_beat
from functools import wraps
import jwt

app = flask.Flask('deploymgr')
app.config['SECRET_KEY'] = 'mysecretkey'

def req_handler():
    @app.route('/deploy', methods=['POST'])
    def deploy():
        # print(flask.request.get_json())
        req = flask.request.get_json()
        if 'port' in req:
            port=req['port']
        else:
            port=None
        output = deploy_util(req['user'],req['appname'],port=port,app_type=req['app_type'])
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
        return flask.jsonify(stop_util(req['name'], req['username'],req['type']))

    @app.route('/restart_service', methods=['POST'])
    def restart():
        req = flask.request.get_json()
        print("Json ",req)
        return flask.jsonify(restart_util(req['username'],req['service_name'], req['service_type']))

    @app.route('/get_services', methods=['GET'])
    def get():
        req = flask.request.get_json()
        print("Json ",req)
        # username in req
        return flask.jsonify(get_services(req))

    @app.route('/test', methods=['POST'])
    def test():
        print("Json ",flask.request.get_json())
        return flask.jsonify({"status":"ok","runtime_id":0})
    app.run(host = '0.0.0.0',port = 8888, threaded=True)
	
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
    # t = threading.Thread(target=heart_beat, args=("deployer",))
    # t.daemon = True
    # t.start()

    t2 = threading.Thread(target=scheduler_consumer, args=())
    t2.daemon = True
    t2.start()
    req_handler()
