from config import db
from flask import abort, make_response
import json
from models import Node, nodes_schema, node_schema
import pickle
import requests


def read_all():
    nodes = Node.query.all()
    return nodes_schema.dump(nodes)


def create(node):
    nodename = node.get("nodename")
    existing_node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if existing_node is None:
        new_node = node_schema.load(node, session=db.session)
        db.session.add(new_node)
        db.session.commit()
        return node_schema.dump(new_node), 201
    else:
        abort(406, f"Node with nodename {nodename} already exists")


def read_one(nodename):
    node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if node is not None:
        return node_schema.dump(node)
    else:
        abort(404, f"Node with nodename {nodename} not found")


def update(nodename, node):
    existing_node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if existing_node:
        update_node = node_schema.load(node, session=db.session)
        existing_node.nodelocation = update_node.nodelocation
        existing_node.nodeip = update_node.nodeip
        existing_node.nodeport = update_node.nodeport
        db.session.merge(existing_node)
        db.session.commit()
        return node_schema.dump(existing_node), 201
    else:
        abort(404, f"Node with nodename {nodename} not found")


def delete(nodename):
    existing_node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if existing_node:
        db.session.delete(existing_node)
        db.session.commit()
        return make_response(f"{nodename} successfully deleted", 200)
    else:
        abort(404, f"Node with nodename {nodename} not found")


def check_for_available_nodes():
    nodes_info = json.loads(requests.get('http://127.0.0.1:8040/api/nodes').text)
    free_nodes_dict = {}
    for node in nodes_info:
        node_type = node['nodetype']
        free_node_content = {}
        free_node_content['id'] = node['id']
        free_node_content['nodename'] = node['nodename']
        free_node_content['nodelocation'] = node['nodelocation']
        if node_type not in free_nodes_dict:
            free_nodes_dict[node_type] = list()
        free_nodes_dict[node_type].append(free_node_content)
    return free_nodes_dict


def get_sensor_nodes_locations():
    '''
    sensor_node_locations = []
    with open('sensorNodeLocations', 'rb') as fp:
        sensor_node_locations = pickle.load(fp)
    return sensor_node_locations
    '''
    nodes_info = json.loads(requests.get('http://127.0.0.1:8040/api/nodes').text)
    locations = set()
    for node in nodes_info:
        locations.add(node['nodelocation'])
    node_locations = list(locations)
    return node_locations
