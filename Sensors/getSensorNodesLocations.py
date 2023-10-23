import pickle
import requests


'''
The controller function of the script that gets all available nodes' locations from OM2MURL!!
'''
def main():
    nodes_url = 'https://iudx-rs-onem2m.iiit.ac.in/resource/nodes'
    sensor_node_locations = set()
    nodes_info = requests.get(nodes_url).json()['results']
    for node_type in nodes_info:
        node_list = nodes_info[node_type]
        for node in node_list:
            tempNode = node
            tempNode = tempNode.split('-')
            for i in tempNode:
                if len(i) == 4:
                    sensor_node_locations.add(i)
                    break
    sensor_node_locations = list(sensor_node_locations)
    with open('sensorNodeLocations', 'wb') as fp:
        pickle.dump(sensor_node_locations, fp)


if __name__ == '__main__':
    main()
