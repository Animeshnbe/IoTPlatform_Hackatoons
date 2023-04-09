from flask import Flask, render_template, request

app = Flask(__name__)

sensor_data = {
    'thermometer': 25,
    'pressure': 50
}

user = {
    'id' : 101
}

@app.route('/', methods=['GET', 'POST'])
def sensor_data_change():
    if request.method == 'POST':
        temperature = request.form['temperature']
        humidity = request.form['humidity']

        sensor_data['thermometer'] = temperature
        sensor_data['pressure'] = humidity

        

    return render_template('app_name.html', sensor_data=sensor_data, user=user)

if __name__ == '__main__':
    app.run(debug=True)