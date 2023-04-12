from flask import render_template, request, redirect, url_for, flash, session,Blueprint
from views.global_ldap_authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask_session import Session

authentication = Blueprint("authentication", __name__)


@authentication.route('/login', methods=['GET','POST'])
def index():

    # initiate the form..
    form = LoginValidation()

    if request.method in ('POST') :
        login_id = request.form['user_name_pid']
        login_password = request.form['user_pid_Password']

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

@authentication.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")
 
