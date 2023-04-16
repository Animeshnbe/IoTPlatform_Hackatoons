from config import db
from flask import abort, make_response
from models import Sensor, sensors_schema, sensor_schema


def read_all():
    sensors = Sensor.query.all()
    return sensors_schema.dump(sensors)


def create(sensor):
    sensorname = sensor.get("sensorname")
    existing_sensor = Sensor.query.filter(Sensor.sensorname == sensorname).one_or_none()
    if existing_sensor is None:
        new_sensor = sensor_schema.load(sensor, session=db.session)
        db.session.add(new_sensor)
        db.session.commit()
        return sensor_schema.dump(new_sensor), 201
    else:
        abort(406, f"Sensor with sensorname {sensorname} already exists")


def read_one(sensorname):
    sensor = Sensor.query.filter(Sensor.sensorname == sensorname).one_or_none()
    if sensor is not None:
        return sensor_schema.dump(sensor)
    else:
        abort(404, f"Sensor with sensorname {sensorname} not found")


def update(sensorname, sensor):
    existing_sensor = Sensor.query.filter(Sensor.sensorname == sensorname).one_or_none()
    if existing_sensor:
        update_sensor = sensor_schema.load(sensor, session=db.session)
        existing_sensor.sensorlatitude = update_sensor.sensorlatitude
        existing_sensor.sensorlongitude = update_sensor.sensorlongitude
        existing_sensor.sensorip = update_sensor.sensorip
        existing_sensor.sensorport = update_sensor.sensorport
        existing_sensor.sensoractive = update_sensor.sensoractive
        db.session.merge(existing_sensor)
        db.session.commit()
        return sensor_schema.dump(existing_sensor), 201
    else:
        abort(404, f"Sensor with sensorname {sensorname} not found")


def delete(sensorname):
    existing_sensor = Sensor.query.filter(Sensor.sensorname == sensorname).one_or_none()
    if existing_sensor:
        db.session.delete(existing_sensor)
        db.session.commit()
        return make_response(f"{sensorname} successfully deleted", 200)
    else:
        abort(404, f"Sensor with sensorname {sensorname} not found")
