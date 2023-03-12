from flask import request, Blueprint, render_template, redirect, flash
from werkzeug.utils import secure_filename
import os
import kafka

monitor = Blueprint("services", __name__)

kafka_server = 'localhost:9092'
topic = 'monitor_nodes'


@monitor.route("/nodeHealthStatus", methods=["GET", "POST"])
def get_nodes_health_status():
    try:
        pass

    except Exception as e:
        raise Exception(str(e))
