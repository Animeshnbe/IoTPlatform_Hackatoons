import threading
import json
import paramiko

LOCK_ALLOC = threading.Lock()
	
def allocate_new_machine():
	global LOCK_ALLOC
	LOCK_ALLOC.acquire()
	result,ip,username,password="","","",""
	file=open("freelist.json")
	free_list=json.load(file)
	if( len(free_list["Servers"])==0):
		result = "NO MACHINE"
	else:
		result = "OK"
		ip = free_list["Servers"][0]["ip"]
		username = free_list["Servers"][0]["username"]
		password = free_list["Servers"][0]["password"]
		port = free_list["Servers"][0]["port"]
		print("setting up new_machine")
		ssh_client =paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh_client.connect(hostname=ip,username=username,password=password)
		ftp_client=ssh_client.open_sftp()
		ftp_client.put("code/ma.py","ma.py")
		ftp_client.close()
		ssh_client.exec_command("python3 ma.py "+str(ip)+" "+str(port)+" "+username+" "+password)
		ssh_client.close()
		del free_list["Servers"][0]
		file.close()
		file=open("freelist.json","w")
		# file.write(json.dumps(free_list))
		# print(free_list)
		json.dump(free_list,file)
		file.close()
	LOCK_ALLOC.release()
	return result,ip,username,password,port