import json


def flow(file_path) :

    with open(file_path, "r") as f:
        data = json.load(f)

    parent_dict = {}
    for d in data:
        if d["type"] == "tab":
            parent_dict[d["id"]] = []
        elif d["type"] == "comment" :
            continue
        elif d["z"] in parent_dict :
            parent_dict[d["z"]].append(d)

    for flow in parent_dict.values():

        if flow["type"] == "http request":
            db["services"].find_one(flow["name"])

    print(parent_dict)

flow("flows3.json")