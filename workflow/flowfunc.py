import json
import pymongo
import flask
import os

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

    
    ordered_dict = {}
    
    for lst in parent_dict.values() :
        ids = set()
        dict_key = {}
        for d in lst :
            ids.add(d["id"])
            dict_key[d["id"]] = d

        for d in lst :
            for item in d["wires"] :
                for i in item :
                    ids.remove(i)

        head = None           
        for i in ids :
            head = i

        if head == None :
            continue 

        ordered = [dict_key[head]]

        i = 0

        while i != len(lst) - 1 :
            for item in ordered[i]["wires"] :
                for j in item :
                    ordered.append(dict_key[j])

            i += 1

        ordered_dict[ordered[0]["id"]] = ordered
        
    print(json.dumps(ordered_dict))

# flow("flows.json")

if __name__ == '__main__':
    client = pymongo.MongoClient(os.getenv("MONGO"))
    db = client['IAS_Global']
    app = flask.Flask('deploymgr')
    @app.route('/accept_workflow', methods=['POST', 'GET'])
    def test():
        print("Json ",flask.request.get_json())
        # print(db["app_runtimes"].find_one({"app":"flasker"}))
        try:
            flow("../flows/flows.json")
            return flask.jsonify({"status":1})
        except:
            return flask.jsonify({"status":0, "message":"Could not start services in your workflow"})
    
    app.run(host = '0.0.0.0',port = 8886, threaded=True)