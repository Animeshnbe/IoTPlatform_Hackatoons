from flask import Flask, request

app = Flask(__name__)

@app.route('/subtract', methods=['POST'])
def subtract_numbers():
    data = request.json
    num1 = data['result']
    result = num1 - 20
    return {'result': result}

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5002, debug=True)