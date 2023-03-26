from flask import request, Blueprint, render_template, redirect, flash
from werkzeug.utils import secure_filename
import os
import kafka

actionPrint = Blueprint("actionModuleServices", __name__)

kafka_server = 'localhost:9092'
topic = 'monitor_nodes'


@actionPrint.route("/nodeHealthStatus", methods=["GET"])
def get_nodes_health_status():
    if request.method == 'GET':
        print("Inside GET Request")
        try:
            # response = monitor.send_node_modules()
            return {}
        except Exception as e:
            raise Exception(str(e))
