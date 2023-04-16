import config
from flask import render_template
from models import Sensor


app = config.connex_app
app.add_api(config.basedir / 'swagger.yml')


@app.route('/')
def home():
    sensors = Sensor.query.all()
    return render_template('home.html', sensors=sensors)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8046, debug=True)
