from flask import request, Blueprint, render_template, redirect, url_for, flash
import authentication
from werkzeug.utils import secure_filename
import os

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
            file.save(os.path.join("./ShoppingCart-main", filename))
            return render_template('signup.html')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
