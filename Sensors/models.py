from config import db, ma
from datetime import datetime
from marshmallow_sqlalchemy import fields


'''
Parameters (id, node_id, content, timestamp)
'''
class Parameters(db.Model):
    __table__name = 'parameters'
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ParametersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parameters
        load_instance = True
        sqla_session = db.session
        include_fk = True


'''
Node (id, name, type, location, ip, port)
'''
class Node(db.Model):
    __tablename__ = 'node'
    id = db.Column(db.Integer, primary_key=True)
    nodename = db.Column(db.String(100), unique=True)
    nodetype = db.Column(db.String(100))
    nodelocation = db.Column(db.String(20))
    nodeip = db.Column(db.String(32))
    nodeport = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parameters = db.relationship(Parameters, backref='node', 
                                 cascade='all, delete, delete-orphan', 
                                 single_parent=True, order_by='desc(Parameters.timestamp)')


class NodeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Node
        load_instance = True
        sqla_session = db.session
        include_relationships = True
    parameters = fields.Nested(ParametersSchema, many=True)


node_schema = NodeSchema()
nodes_schema = NodeSchema(many=True)
parameters_schema = ParametersSchema()
all_parameters_schema = ParametersSchema(many=True)
