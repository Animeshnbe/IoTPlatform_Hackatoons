from flask import Flask, request

app = Flask(__name__)

@app.route('/exponentiate', methods=['POST'])
def exponentiate_numbers():
    data = request.json
    num1 = data['num1']
    num2 = data['num2']
    result = num1 ** num2
    return {'result': result}

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5005, debug=True)