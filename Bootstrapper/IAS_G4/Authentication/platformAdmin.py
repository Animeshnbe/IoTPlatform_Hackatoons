from flask import render_template, request, redirect, url_for, flash, session, Blueprint

platformAdmin = Blueprint("platformAdmin", __name__)


@platformAdmin.route('/platformAdminHome', methods=['GET','POST'])
def platformAdminHome():
    # if not session.get("name"):
    #     return redirect("/login")
    return render_template('platformAdminHome.html')