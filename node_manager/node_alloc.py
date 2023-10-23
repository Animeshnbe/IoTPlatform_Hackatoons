import threading
import json
import paramiko
import flask
from prometheus_flask_exporter import PrometheusMetrics

LOCK_ALLOC = threading.Lock()

def allocate_new_machine(port=None):
	global LOCK_ALLOC
	LOCK_ALLOC.acquire()
	ip,username,password="","",""
	with open("vm_list.json") as file:
		free_list=json.load(file)
	if( len(free_list)==0):
		resp = {"msg":"NO MACHINE"}
	else:
		print("setting up new_machine")
		resp = {"msg":"SERVERS NOT REACHABLE"}
		for vm in free_list:
			ip = vm["ip"]
			username = vm["username"]
			password = vm["password"]
			# port = free_list[0]["port"]
			try:
				ssh_client =paramiko.SSHClient()
				ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				print("connecting to ",ip)
				ssh_client.connect(hostname=ip,username=username,password=password)
				ftp_client=ssh_client.open_sftp()
				ftp_client.put("machine_stats.py","ma.py")
				ftp_client.close()
				_, stdout, _ = ssh_client.exec_command("python3 ma.py")
				stdout = stdout.read().decode()
				stdout = [float(f) for f in stdout.split(",")]
				print(stdout)
				ssh_client.exec_command("rm ma.py")
				if stdout[0]<2 and stdout[1]<0.5:
					continue
				if port is not None:
					_, stdout, stderr = ssh_client.exec_command("netstat -na | grep :"+port)
					if len(stdout.read().decode())>0:
						continue
					channel = ssh_client.invoke_shell()
					# Send the sudo command
					channel.send('sudo -S -p "" ufw allow '+port+'\n')
					# Wait for the sudo password prompt
					while not channel.recv_ready():
						pass
					# Send the sudo password
					channel.send(password + '\n')
					# Wait for the command to finish executing
					while not channel.recv_ready():
						pass
					output = channel.recv(1024).decode('utf-8')
					print(output)
				# ssh_client
				ssh_client.close()
				resp = {"msg":"OK","ip":ip,"username":username,"password":password}
				free_list.remove(vm)
				free_list.append(vm)
				# print(free_list)
				with open("vm_list.json","w") as file:
					file.write(json.dumps(free_list))		
				break
			except Exception as ex:
				print("Could not reach VM ",ex)
			
	LOCK_ALLOC.release()
	return resp

# print(allocate_new_machine())
if __name__ == '__main__':
	app = flask.Flask('nodemgr')
	metrics = PrometheusMetrics(app)
	@app.route('/', methods=['POST', 'GET'])
	def alloc():
		try:
			print("Json ",flask.request.get_json())
			req = flask.request.get_json()
			if 'port' in req:
				return flask.jsonify(allocate_new_machine(req['port']))
			return flask.jsonify(allocate_new_machine())
		except Exception as ex:
			return flask.jsonify({"msg":"API error "+ex})
		
	metrics.register_default(
		metrics.counter(
			'by_path_counter', 'Request count by request paths',
			labels={'path': lambda: flask.request.path}
		)
	)
	app.run(host = '0.0.0.0',port = 8887, threaded=True)