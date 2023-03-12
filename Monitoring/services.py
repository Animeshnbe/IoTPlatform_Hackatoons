from flask import request, Blueprint, render_template, redirect, flash
from werkzeug.utils import secure_filename
import os

services = Blueprint("services", __name__)


@services.route("/nodeHealthStatus", methods=["GET", "POST"])
def get_nodes_health_status():
    try:
        pass

    except Exception as e:
        raise Exception(str(e))
