from flask import render_template, request, redirect, url_for, flash, session
from views.global_ldap_authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer

# app.secret_key = "testing"

# client = pymongo.MongoClient(host="localhost", port=27017)




app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/login', methods=['GET','POST'])
def index():

    # initiate the form..
    form = LoginValidation()

    if request.method in ('POST') :
        # login_id = form.user_name_pid
        login_id = request.form['user_name_pid']
        # print(login_id)
        # login_password = form.user_pid_Password
        login_password = request.form['user_pid_Password']
        # print(login_password)

        # create a directory to hold the Logs
        login_msg = global_ldap_authentication(login_id, login_password)

        # validate the connection
        if login_msg == "Success":
            success_message = f"*** Authentication Success "
            session["name"] = request.form.get("user_name_pid")
            return redirect("/")

        else:
            error_message = f"*** Authentication Failed - {login_msg}"
            return render_template("error.html", error_message=str(error_message))

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")
 

@app.route('/developerHome', methods=['GET','POST'])
def developerHome():
    # if not session.get("name"):
    #     return redirect("/login")
    return render_template('developerHome.html')


@app.route('/')
def home():
    if not session.get("name"):
        return redirect("/login")
    if session.get("name") == "developer":
        return redirect("/developerHome")
    if session.get("name") == "admin":
        return redirect("/adminHome")

    return "HOME"



# @app.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
        




if __name__ == '__main__':
    app.run(debug=True,port=5005)