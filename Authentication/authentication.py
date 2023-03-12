from flask import request, Blueprint
from mongo_utility import MongoUtility
# from db_conn import DBConnection
import json

projects = Blueprint("authentication", __name__)
mongo_port = 27017
mongo_host = "localhost"
mongo_username = "root"
mongo_password = "dQFdN+kPl+I+hLKQEivugHTuzjgpERepxmUt6qMu3I51Kjljv9qGTeMgobr724dg"


def login(username, password):
    try:
        user_authenticated = False
        # username = input_json["username"]
        # password = input_json["password"]
        user_json = {"username": username}
        mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        user_record = mongo_utility.find_json(user_json, "iot", "users")
        print("user_record : ", user_record)
        print("user_record[0]: ",user_record[0])
        fetched_user_password = user_record[0].get("password", "")
        if fetched_user_password == password:
            user_authenticated = True
        print("fetched_user_id : ", user_authenticated)

        return user_authenticated

    except Exception as e:
        print("Error while getting POST request : ", e)


def sign_up_user(input_json):
    try:
        user_added = False
        mongo_utility = MongoUtility(_mongo_port=mongo_port, _mongo_host=mongo_host)
        user_data = mongo_utility.insert_one(input_json, "iot", "users")
        if user_data:
            user_added = True
        return user_added

    except Exception as e:
        print("Error while getting POST request : ", e)


# @projects.route("/database_multi_insert", methods=["POST"])
# def multi_insert_data_service():
#     if request.method == "POST":
#         try:
#             new_json = json.loads(request.get_data())
#             print("new_json : ", new_json)
#             records = new_json["data"]
#             print("records : ", records)
#             print("records : ", type(records))
#             records = records.strip('][').split(', ')
#             print("records : ", type(records))
#             print("records : ", records)
#             records_to_insert = [(4, 'LG', 800), (5, 'One Plus 6', 950), (7, 'Nokia 7', 800)]
#             db_ops.insert_multiple_records(records_to_insert)
#             return "Your records inserted successfully"
#         except Exception as e:
#             print("Error while getting POST request : ", e)
#     else:
#         return "Not a POST request"
#
#
# @projects.route("/database_single_insert", methods=["POST"])
# def insert_data_service():
#     if request.method == "POST":
#         try:
#             new_json = json.loads(request.get_data())
#             print("new_json : ", new_json)
#             # record_to_insert = (13, 'Note 9', 1400)
#             record_to_insert = (new_json["id"], new_json["model"], new_json["price"])
#             db_ops.insert_one_record(record_to_insert)
#             return "Your record is inserted successfully"
#         except:
#             print("Error while getting POST request")
#     else:
#         return "Not a POST request"
#
#
# @projects.route("/database_single_update", methods=["POST"])
# def update_data_service():
#     if request.method == "POST":
#         try:
#             new_json = json.loads(request.get_data())
#             print(new_json)
#             db_ops.update_one_record(new_json["price"], new_json["id"])
#             return "Your record is updated successfully"
#         except Exception as e:
#             print("Error while getting POST request : ", e)
#
#     else:
#         return "Not a POST request"
#
#
# @projects.route("/database_single_delete", methods=["POST"])
# def delete_data_service():
#     if request.method == "POST":
#         try:
#             new_json = json.loads(request.get_data())
#             print(new_json)
#             db_ops.delete_record(new_json["id"])
#             return "Your record is deleted successfully"
#         except Exception as e:
#             print("Error while getting POST request : ", e)
#
#     else:
#         return "Not a POST request"
#
#
# @projects.route("/database_inner_join", methods=["GET"])
# def inner_join_service():
#     db_ops.db_inner_join()
#     return "Inner Joined worked successfully"
