from flask import Flask, request
from flask_cors import CORS
import monitorServices
import threading
from monitor import node_monitoring
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.register_blueprint(monitorServices.monitorPrint)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def route():
    return "------------------ Monitoring Tool ----------------------"


if __name__ == '__main__':
    metrics = PrometheusMetrics(app)
    t1 = threading.Thread(target=node_monitoring)
    t1.daemon = True
    t1.start()
    metrics.register_default(
        metrics.counter(
            'by_path_counter', 'Request count by request paths',
            labels={'path': lambda: request.path}
        )
    )
    app.run(host='0.0.0.0', port=9823, debug=True, threaded=True, use_reloader=False)
