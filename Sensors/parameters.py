from config import db
from flask import abort, make_response
from models import Parameters, Node, parameters_schema, all_parameters_schema


def read_all():
    parameters = Parameters.query.all()
    return all_parameters_schema.dump(parameters)


def read_one(parameter_id):
    parameter = Parameters.query.get(parameter_id)
    if parameter is not None:
        return parameters_schema.dump(parameter)
    else:
        abort(404, f"Parameter with ID {parameter_id} not found")


def update(parameter_id, parameter):
    existing_parameter = Parameters.query.get(parameter_id)
    if existing_parameter:
        update_parameter = parameters_schema.load(parameter, session=db.session)
        existing_parameter.content = update_parameter.content
        db.session.merge(existing_parameter)
        db.session.commit()
        return parameters_schema.dump(existing_parameter), 201
    else:
        abort(404, f"Parameter with ID {parameter_id} not found")


def delete(parameter_id):
    existing_parameter = Parameters.query.get(parameter_id)
    if existing_parameter:
        db.session.delete(existing_parameter)
        db.session.commit()
        return make_response(f"{parameter_id} successfully deleted", 204)
    else:
        abort(404, f"Parameter with ID {parameter_id} not found")


def create(parameter):
    node_id = parameter.get('node_id')
    node = Node.query.get(node_id)
    if node:
        new_parameter = parameters_schema.load(parameter, session=db.session)
        node.parameters.append(new_parameter)
        db.session.commit()
        return parameters_schema.dump(new_parameter), 201
    else:
        abort(404, f"Node not found for ID: {node_id}")
