from flask import Flask
from flask_cors import CORS
import services

app = Flask(__name__)
app.register_blueprint(services.services)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def route():
    return "------------------ Monitoring Tool ----------------------"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9823, debug=True, threaded=True, use_reloader=False)