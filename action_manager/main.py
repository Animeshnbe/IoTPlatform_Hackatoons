from flask import Flask, request
from flask_cors import CORS
import threading
import actionModuleServices
from heartBeat import heart_beat
from prometheus_flask_exporter import PrometheusMetrics


# from actionModuleServices import fetch_nodes_status

app = Flask(__name__)
app.register_blueprint(actionModuleServices.actionPrint)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def route():
    return "------------------ Action Manager Tool ----------------------"


if __name__ == '__main__':
    metrics = PrometheusMetrics(app)
    module_name = "action_manager"
    t = threading.Thread(target=heart_beat, args=(module_name,))
    t.daemon = True
    t.start()

    metrics.register_default(
        metrics.counter(
            'by_path_counter', 'Request count by request paths',
            labels={'path': lambda: request.path}
        )
    )
    app.run(host='0.0.0.0', port=9825, debug=True, threaded=True, use_reloader=False)
