from config import db, ma
from datetime import datetime
from marshmallow_sqlalchemy import fields


class Parameters(db.Model):
    __table__name = 'parameters'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'))
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ParametersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parameters
        load_instance = True
        sqla_session = db.session
        include_fk = True


class Sensor(db.Model):
    __tablename__ = 'sensor'
    id = db.Column(db.Integer, primary_key=True)
    sensorname = db.Column(db.String(32), unique=True)
    sensortype = db.Column(db.String(32))
    sensorlatitude = db.Column(db.Integer)
    sensorlongitude = db.Column(db.Integer)
    sensorip = db.Column(db.String(32))
    sensorport = db.Column(db.Integer)
    sensoractive = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parameters = db.relationship(Parameters, backref='sensor', 
                                 cascade='all, delete, delete-orphan', 
                                 single_parent=True, order_by='desc(Parameters.timestamp)')


class SensorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sensor
        load_instance = True
        sqla_session = db.session
        include_relationships = True
    parameters = fields.Nested(ParametersSchema, many=True)


sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)
parameters_schema = ParametersSchema()
all_parameters_schema = ParametersSchema(many=True)
