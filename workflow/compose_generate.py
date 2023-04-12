import os
import yaml

import json

def flow(file_path):

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

flow("flows.json")

num_apps = 3 

services = {}
for i in range(1, num_apps+1):
    app_name = f'app{i}'
    services[app_name] = {
        'build': {
            'context': f'./{app_name}',
        },
        'ports':[
            f'{5000+i}:{5000+i}'
        ],
        'networks':[
            'my-network'
        ]
    }

networks = {
    'my-network': {
                'driver': 'bridge'
            }
}

compose_data = {
    'version': '3',
    'services': services,
    'networks': networks,
}

with open('docker-compose.yml', 'w') as f:
    yaml.dump(compose_data, f, sort_keys=False)