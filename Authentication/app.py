from flask import render_template, request, redirect, url_for, flash, session
from views.global_ldap_authentication import *
from forms.LoginForm import *
from flask_cors import CORS, cross_origin
from flask_session import Session
import developer
import authentication
import platformAdmin


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# app.secret_key = "testing"

# client = pymongo.MongoClient(host="localhost", port=27017)

app.register_blueprint(developer.developer)
app.register_blueprint(authentication.authentication)
app.register_blueprint(platformAdmin.platformAdmin)

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
    app.run(host="0.0.0.0",debug=True,port=5005)


import developer
