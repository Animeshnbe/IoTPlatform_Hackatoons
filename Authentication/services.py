from flask import request, Blueprint, render_template, redirect, url_for, flash
import authentication
from werkzeug.utils import secure_filename
import os
from azure.storage.blob import BlobServiceClient

services = Blueprint("services", __name__)


@services.route("/login", methods=["GET", "POST"])
def authenticate():
    try:
        if request.method == 'POST':
            try:
                # input_json = json.loads(request.get_data())
                username = request.form["email"]
                password = request.form["password"]
                loginresponse = authentication.login(username, password)
                print("loginresponse : ", loginresponse)
                response = dict()
                response['status'] = "OK"
                response['message'] = loginresponse
                if loginresponse:
                    return render_template('/dashboard')
                return render_template('signup.html')
                # return f"<h1>{username}</h1>"
            except Exception as e:
                raise Exception(str(e))
        else:
            return render_template('login.html')

    except Exception as e:
        raise Exception(str(e))


@services.route("/index", methods=["GET", "POST"])
def index():
    return '<h1>Index</h1>'


@services.route("/signUp", methods=["POST", "GET"])
def sign_up():
    try:
        if request.method == 'POST':
            try:
                # input_json = json.loads(request.get_data())
                username = request.form["username"]
                password = request.form["password"]
                email = request.form["email"]
                role = request.form["role"]
                phone_no = request.form["phone_no"]
                input_json = dict(username=username, password=password, email=email, role=role, phone_no=phone_no)
                sign_up_response = authentication.sign_up_user(input_json)
                if sign_up_response:
                    return render_template('login.html')

                return render_template('signup.html')

            except Exception as e:
                raise Exception(str(e))
        else:
            return render_template('signup.html')

    except Exception as e:
        raise Exception(str(e))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ["zip"]


@services.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        print("file : ", file)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print("filename ", filename)
            connect_str = "DefaultEndpointsProtocol=https;AccountName=aman0ias;AccountKey=ejuMHDXoYsp4ktNpndJTqrC0QXgEi7DCv0cJiK94R6ZhMYZa+VmKnYcTNv3T6qIc/qoYnnZbGZPg+AStGotFJA==;EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            container_name = "zipstorage"
            container_client = blob_service_client.get_container_client(container_name)
            file_path = "/home/priyanshu/Documents/IoTPlatform_Hackatoons-team2/Authentication/" + filename
            file_name = os.path.basename(file_path)
            blob_client = container_client.get_blob_client(blob=file_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data)
            return render_template('signup.html')
