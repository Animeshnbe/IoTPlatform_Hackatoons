from flask import request, Blueprint, render_template, redirect, flash
from werkzeug.utils import secure_filename
import os
import kafka
from actionManagerHandler import action_manager_request_handler, email_handler, listening_to_sensor_manager
from notificationUtility import send_email

actionPrint = Blueprint("actionModuleServices", __name__)


# kafka_server = 'localhost:9092'
# topic = 'monitor_nodes'


@actionPrint.route("/actionManagerAPI", methods=["POST"])
def action_manager_request_service():
    if request.method == 'POST':
        print("Inside POST Request")
        try:
            input_json = request.get_json()
            print(type(input_json))
            action_manager_request_handler(input_json)
            # response = listening_to_sensor_manager()
            response = dict(message="success")
            return response
        except Exception as e:
            raise Exception(str(e))


@actionPrint.route("/emailAPI", methods=["POST"])
def email_API_service():
    if request.method == 'POST':
        print("Inside POST Request")
        try:
            input_json = request.get_data()
            response = email_handler(input_json["subject"], input_json.get("text", ""), input_json.get("email", ""))
            return response
        except Exception as e:
            raise Exception(str(e))
