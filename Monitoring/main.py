from flask import Flask
from flask_cors import CORS
import services
import threading
from monitor import fetch_nodes_status

app = Flask(__name__)
app.register_blueprint(services.monitor)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def route():
    return "------------------ Monitoring Tool ----------------------"


if __name__ == '__main__':
    send_logs_thread = threading.Thread(target=fetch_nodes_status)
    send_logs_thread.start()

    app.run(host='0.0.0.0', port=9823, debug=True, threaded=True, use_reloader=False)
