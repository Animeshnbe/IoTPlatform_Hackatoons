from flask import render_template, request, redirect, url_for, flash, session, Blueprint

developer = Blueprint("developer", __name__)


@developer.route('/developerHome', methods=['GET','POST'])
def developerHome():
    # if not session.get("name"):
    #     return redirect("/login")
    return render_template('developerHome.html')