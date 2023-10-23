from apscheduler.schedulers.background import BackgroundScheduler
from azure.storage.blob import BlobServiceClient, BlobClient, generate_blob_sas, BlobSasPermissions
import config
from datetime import datetime, timedelta
from flask import render_template, request
from models import Node
import os
from time import sleep


app = config.connex_app
app.add_api(config.basedir / 'swagger.yml')
flask_app = app.app


@app.route('/')
def home():
    config.db.create_all()
    nodes = Node.query.all()
    return render_template('home.html', nodes=nodes)


@app.route('/stream')
def stream():
    '''
    Generator Function that yields new lines in a file
    '''
    def generate():
        with open('sensormanager.log') as logfile:
            logfile.seek(0, os.SEEK_END)
            while True:
                line = logfile.readline()
                # sleep if file hasn't been updated
                if not line:
                    sleep(0.1)
                    continue
                yield line
    return flask_app.response_class(generate(), mimetype='text/plain')


'''
Storage of log files in Azure Blob Storage
'''
def store_logs():
    try:
        account_name = 'amanias'
        account_key = 'VtqTdX+sG1/dkhqhHT80jXUGULqJKlBsn++AmB2NnPvefgjyGggJ3dIo8wNBOudu6EdQwicUSEqd+AStbhmWZg=='
        container_name = 'sensormanager'
        # create a client to interact with blob storage
        connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        # use the client to connect to the container
        container_client = blob_service_client.get_container_client(container_name)
        # get a list of all blob files in the container
        blob_list = []
        for blob_i in container_client.list_blobs():
            blob_list.append(blob_i.name)
        print("BLOB list : ", blob_list)
        for blob_i in blob_list:
            # generate a shared access signature for each blob file
            sas_i = generate_blob_sas(account_name=account_name,
                                      container_name=container_name,
                                      blob_name=blob_i,
                                      account_key=account_key,
                                      permission=BlobSasPermissions(read=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1))
            #sas_url = 'https://' + account_name + '.blob.core.windows.net/' + container_name + '/' + blob_i + '?' + sas_i
            try:
                file_path = 'sensormanager.log'
                print("Inside Azure Log File Write: ", file_path)
                with open(file=file_path, mode="rb") as data:
                    blob_client = container_client.upload_blob(name="sensormanager.log", data=data, overwrite=True)
                    print("Blob client : ", blob_client)
                open(file_path, "w").close()
            except Exception as e:
                return f'Error reading file: {str(e)}'
    except Exception as e:
        print(e)
    print('Data appended successfully')


if __name__ == '__main__':
    # Configure and start the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(store_logs, 'interval', minutes=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=8040, debug=True)
