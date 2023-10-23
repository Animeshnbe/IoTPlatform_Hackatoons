from kafka import KafkaProducer
from kafka import KafkaConsumer
import schedule 
import time 
import threading 
from flask import Flask,request,jsonify
import random
import json
import requests
import argparse
import datetime
import pickle
import time
import os
from dotenv import load_dotenv
from heartBeat import heart_beat
app = Flask(__name__)

service_life_cycle_ip = "10.2.132.235"
service_life_cycle_port = 8888
Myport = 5053

load_dotenv()
kafka_host = os.getenv('kafka_host')
# Create a Kafka producer
producer = KafkaProducer(bootstrap_servers=['10.2.135.69:9092'], value_serializer=lambda x: json.dumps(x).encode('utf-8'))
# response = {"username":"username","applicationname":"application_id","servicename":"servicename","serviceId":"sid", "type":"start"}
# producer.send("sch_dep", response)

# producer = KafkaProducer(
#         bootstrap_servers=[kafka_host],
#         value_serializer=lambda m: json.dumps(m).encode('ascii'))
    # for _,row in df.iterrows():
# while True:
        # call_sensor_instance
# producer.send("sch_dep", key=None,value=response)
# time.sleep(30)
    # sleep(rate)

# consumer = KafkaConsumer('sch_dep', bootstrap_servers=['192.168.137.51:19092'],
#                                 value_deserializer=lambda x: json.loads(x.decode('utf-8')))
# while(1):
#     for m in consumer:
#         print(m)
#         time.sleep(10)

# Produce a message to a topic and wait for acknowledgement
topic = 'sch_dep'

schedules = []
schedules_ = []

# schedules_ = [
#         {'service_id' : '1', 'request' : {"username": "A",
# 		"application_id": "100",
# 		"servicename": "XYZ",
# 		"Repeat": "True",
# 		"day": None,
# 		"Schedule_time":"18:20:00",
#         "Stop_time":"18:22:00",
#         "priority":1,
# 		"period":"30",
#         "duration":"20"}}

        # ,
        # {'service_id' : '2', 'request' : {"username": "B",
		# "application_id": "101",
		# "servicename": "aaa",
		# "Repeat": "False",
		# "day": None,
		# "Schedule_time":"15:58:00",
        # "Stop_time":"15:59:00",
        # "priority":1,
		# "period":"5"}}
        # ,
        # {'service_id' : '3', 'request' : {"username": "C",
		# "application_id": "102",
		# "servicename": "bbb",
		# "Repeat": "False",
		# "day": "sunday",
		# "Schedule_time":"15:52:00",
        # "Stop_time":"15:53:00",
        # "priority":0,
		# "period":"5"}}
        # ,
        # {'service_id' : '4', 'request' : {"username": "D",
		# "application_id": "103",
		# "servicename": "ccc",
		# "Repeat": "False",
		# "day": None,
		# "Schedule_time":"15:54:00",
        # "Stop_time":"15:55:00",
        # "priority":0,
		# "period":"5"}}
        # ]
started = {'key' : 'Jagdish', 'name' : 'Jagdish Pathak',
'age' : 50, 'pay' : 50000}
  
# database
db1 = {}
db1['schedules'] = schedules
db1['started'] = started
  
# For storing
b = pickle.dumps(db1)

DUMPING_DELAY_IN_3_SECS = 1
# def time_add(time,sec_to_add) :
#      hr = int(str(time).split(":")[0])
#      mn = int(str(time).split(":")[1])
#      sc = int(str(time).split(":")[2])
#      sc = (sc+sec_to_add)
#      hr = (hr + mn+ int(sc/3600))%24
#      sc=sc%3600
#      hr = str(hr)
#      mn = str(mn)
#      if(len(hr)==1):
#          hr="0"+hr
#      if(len(mn)==1):
#          mn="0"+mn
#      return hr+":"+mn

class Scheduler:
    def __init__(self) -> None:
        self.job_dict = {}
        self.main_service_id_dict={}
        self.single_instances ={} #
        self.started = {} #done
        self.loop_schedules=[] #done
        self.main_id_sch_id={}
        pass

    def pending_jobs(self):
        while True: 
            schedule.run_pending() 
            time.sleep(10)
    def send_request_to_service_life_cyle(self,username,application_id,servicename,service_instance_id,type_):
        # print(username,application_id,servicename,service_instance_id,self.main_service_id_dict[service_instance_id])
        response = {"username":username,"applicationname":application_id,"servicename":servicename,"serviceId":self.main_service_id_dict[service_instance_id], "type":""}
        # print(response)
        if type_=="start":
            print("start",response)
            print('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/test')
            response['type'] = "start"
            future = producer.send(topic, response)
            result = future.get(timeout=60)
            # res = requests.post('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/test', json=json.dumps(response))
        else:
            print("stop",response)
            response['type'] = "stop"
            future = producer.send(topic, response)
            result = future.get(timeout=60)
            # res = requests.post('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/test', json=json.dumps(response))

    def getInfo(self):
        # dbfile = open("/home/sch_data.pickle","rb")
        db = pickle.loads(b)
        # print(db)
        schedules_ = db["schedules"]
        started = db["started"]
        return schedules_ , started
        pass
    def run(self):
        t1 = threading.Thread(target=self.pending_jobs) 
        t1.start()
    
    def exit_service(self,service_instance_id):
        service_instance_id,username,application_id,servicename = service_instance_id[0],service_instance_id[1],service_instance_id[2],service_instance_id[3]
        print("+MSG TO SLCM TO STOP \t\t",service_instance_id)
        #send request to service life cycle manager to cancel service 
        self.send_request_to_service_life_cyle(username,application_id,servicename,service_instance_id,"stop")
        print(self.started)
        del self.started[service_instance_id]
        schedule.cancel_job(self.job_dict[service_instance_id])
        # del self.job_dict[service_instance_id]
    
    def exit_service_parent(self,job_id):
        print("Removed - ",job_id)
        schedule.cancel_job(job_id)
        return schedule.CancelJob

    def run_service(self,service_detail):
        username,application_id,servicename,end,service_instance_id = service_detail[0],service_detail[1],service_detail[2],service_detail[3],service_detail[4]
        print("+MSG TO SLCM TO START \t\t",service_instance_id)
        #send request to service life cycle manager to start service
        self.send_request_to_service_life_cyle(username,application_id,servicename,service_instance_id,"start")
        data = {
               "service_id": service_instance_id,
               "username":username,
               "application_id":application_id,
               "servicename":servicename,
               "end":end
        }
        self.started[service_instance_id]=data
        job_id = schedule.every().day.at(end).do(self.exit_service,((service_instance_id,username,application_id,servicename))) 
        self.job_dict[service_instance_id]=job_id
        
    def run_service_period(self,service_detail, duration):
        username,application_id,servicename,end,service_instance_id = service_detail[0],service_detail[1],service_detail[2],service_detail[3],service_detail[4]
        print("+MSG TO SLCM TO START \t\t",service_instance_id)
        #send request to service life cycle manager to start service
        self.send_request_to_service_life_cyle(username,application_id,servicename,service_instance_id,"start")

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        print("curr: ", current_time)
        print("duration: ", duration)
        
        time_change = datetime.timedelta(seconds=int(duration))
        Stop_time_1 = now + time_change
        print("stop time:", Stop_time_1)
        data = {
               "service_id": service_instance_id,
               "username":username,
               "application_id":application_id,
               "servicename":servicename,
               "end":Stop_time_1
        }
        self.started[service_instance_id]=data

        n11 = str(Stop_time_1)
        n1 = n11[11:19]
        job_id = schedule.every().day.at(n1).do(self.exit_service,((service_instance_id,username,application_id,servicename))) 
        self.job_dict[service_instance_id]=job_id

    def run_service1(self,service_detail):
        username,application_id,servicename,end,service_instance_id = service_detail[0],service_detail[1],service_detail[2],service_detail[3],service_detail[4]
        print("+MSG TO SLCM TO START \t\t",service_instance_id)
        #send request to service life cycle manager to start service
        self.send_request_to_service_life_cyle(username,application_id,servicename,service_instance_id,"start")
        data = {
               "service_id": service_instance_id,
               "username":username,
               "application_id":application_id,
               "servicename":servicename,
               "end":end
        }
        self.started[service_instance_id]=data
        if(service_instance_id in self.single_instances.keys()):
            del self.single_instances[service_instance_id] 
        
        print("Running everyday\n")
        print("end: ", end)
        print(type(end))
        job_id = schedule.every().day.at(end).do(self.exit_service,((service_instance_id,username,application_id,servicename))) 
        try:
            if(self.job_dict[service_instance_id]):
                # print("here")
                schedule.cancel_job(self.job_dict[service_instance_id])
        except:
            pass
        self.job_dict[service_instance_id]=job_id
        pass

    def run_service2(self,Schedule_time,day,service_detail):
        service_instance_id = service_detail[4]
        self.single_instances[service_instance_id]=request_
        job_id = None
        if(day=="monday"):
            job_id = schedule.every().monday.at(Schedule_time).do( self.run_service1,(service_detail))
        elif(day=="tuesday"):
            job_id = schedule.every().tuesday.at(Schedule_time).do( self.run_service1,(service_detail))
        elif(day=="wednesday"):
            job_id = schedule.every().wednesday.at(Schedule_time).do( self.run_service1,(service_detail))
        elif(day=="thursday"):
            job_id = schedule.every().thursday.at(Schedule_time).do( self.run_service1,(service_detail))
        elif(day=="friday"):
            job_id = schedule.every().friday.at(Schedule_time).do( self.run_service1,(service_detail))
        elif(day=="saturday"):
            job_id = schedule.every().saturday.at(Schedule_time).do( self.run_service1,(service_detail))
        else:
            print("Sunday\n")
            job_id = schedule.every().sunday.at(Schedule_time).do( self.run_service1,(service_detail))
        self.job_dict[service_instance_id]=job_id
        pass

    def run_service3(self,Schedule_time,day,service_detail):
        service_instance_id = service_detail[4]
        self.single_instances[service_instance_id]=request_
        job_id = schedule.every().day.at(Schedule_time).do( self.run_service1,(service_detail))
        self.job_dict[service_instance_id]=job_id
        pass

    def run_service4(self,period,duration,end_time,service_detail):
        service_instance_id = service_detail[4]
        self.loop_schedules.append({"service_id":service_instance_id,"request": request_})
        interval = int(period)
        end = end_time

        job_id = schedule.every(interval).seconds.do( self.run_service_period,service_detail, duration)
        self.job_dict[service_instance_id]=job_id
        job_id1 = schedule.every().day.at(end_time).do(self.exit_service_parent,(job_id))
        pass

    def run_service5(self,Schedule_time,day,service_detail):
        service_instance_id = service_detail[4]
        self.loop_schedules.append({"service_id":service_instance_id,"request": request_})
        if(day=="monday"):
            job_id = schedule.every().monday.at(Schedule_time).do( self.run_service,(service_detail))
        elif(day=="tuesday"):
            job_id = schedule.every().tuesday.at(Schedule_time).do( self.run_service,(service_detail))
        elif(day=="wednesday"):
            job_id = schedule.every().wednesday.at(Schedule_time).do( self.run_service,(service_detail))
        elif(day=="thursday"):
            job_id = schedule.every().thursday.at(Schedule_time).do( self.run_service,(service_detail))
        elif(day=="friday"):
            job_id = schedule.every().friday.at(Schedule_time).do( self.run_service,(service_detail))
        elif(day=="saturday"):
            job_id = schedule.every().saturday.at(Schedule_time).do( self.run_service,(service_detail))
        else:
            job_id = schedule.every().sunday.at(Schedule_time).do( self.run_service,(service_detail))
        pass
    
    def StartSchedulling(self,request_,s_id=None):
        username = request_["username"]
        application_id = request_["application_id"]
        servicename = request_["servicename"]
        repeat = request_["Repeat"]
        day = request_["day"]
        Schedule_time = request_["Schedule_time"]
        end = request_["Stop_time"]
        period = request_["period"]
        priority = request_["priority"]
        duration = request_["duration"]
        main_service_id = username+"_"+application_id+"_"+servicename
        
        service_instance_id = s_id

        if service_instance_id is None:
            service_instance_id=username+"_"+application_id+"_"+servicename+"_"+str(random.randrange(10000))

        self.main_service_id_dict[service_instance_id]=main_service_id
        self.main_id_sch_id[main_service_id] = service_instance_id

        result = "OK"
        if(str(repeat)=="False"):
            print("single instance ",bool(repeat))
            if(priority==1 and day is None): # every day
                print("1")
                self.run_service1((username,application_id,servicename,end,s_id))
            elif priority==1 and day is not None: #specific day
                print("2")
                self.run_service2(Schedule_time,day,(username,application_id,servicename,end,s_id))
            elif priority!=1 and day is not None: # specific day
                print("3")
                self.run_service2(Schedule_time,day,(username,application_id,servicename,end,s_id))
            else: # every day
                print("4")
                self.run_service1((username,application_id,servicename,end,s_id))

        elif day is None and period is not None:                                            #everyday
            print("5")
            self.run_service4(period,duration,end,(username,application_id,servicename,end,s_id))
        # elif day is not None:
        #     print("6")
        #     self.run_service5(Schedule_time,day,(username,application_id,servicename,end,s_id))
        else:
            result = "ERROR : wrong scheduling format"
        return result,s_id
        pass

    def stop_all_started_at_their_Stop_time(self):
        # for key in self.started.keys():
        #     service_instance_id,username,application_id,service_name,end = self.started[key]["service_id"],self.started[key]["username"],self.started[key]["application_id"],self.started[key]["service_name"],self.started[key]["end"]
        #     job_id = schedule.every().day.at(end).do(self.exit_service,((service_instance_id,username,application_id,service_name))) 
        #     self.job_dict[service_instance_id]=job_id
        #     # del self.started[service_instance_id]
        #     self.main_service_id_dict[service_instance_id] = username+"_"+application_id+"_"+service_name
        #     self.main_id_sch_id[username+"_"+application_id+"_"+service_name]=service_instance_id
        pass

# @app.route('/schedule_service', methods=['GET', 'POST'])
# def schedule_service():
#     content = request.get_json()
    
#     res = "OK"
#     # print(content)
#     # print(type(content))
#     if(content["action"]=="Stop"):
#         id = 1
#         print("+MSG TO SLCM TO STOP ",id)

#     else:
#         if(content["action"]=="Start"):
#             print("start")

#     return {"result":res}

# def get_schedules():
#     url = 'http://10.2.128.235:5000/get'
#     while(True):
#         response = requests.get(url)
#         s1 = json.loads(response.content)
#         if(s1):
#             schedules_.append(s1)
#         else:
#             time.sleep(5)

# t1 = threading.Thread(target = get_schedules)
# t1.start()


# sch = []
def get_schedules():
    # Consume messages from a topic
    for message in consumer:
        schedules_.extend(message[6])
        print("1kja")
        print("message", message[6])
        print(message.topic, message.partition, message.offset, message.value)

# Create a Kafka consumer
consumer = KafkaConsumer('appmgr_sch', bootstrap_servers=['10.2.135.69:9092'],
                                value_deserializer=lambda x: json.loads(x.decode('utf-8')), auto_offset_reset='latest')


t1 = threading.Thread(target = get_schedules)
t1.start()

#Heartbeat
t2 = threading.Thread(target = heart_beat, args=("Scheduler",))
t2.daemon = True
t2.start()

sch = Scheduler()
sch.run()
# schedules1_ , started = sch.getInfo()
sch.loop_schedules == schedules_
sch.started = started
while(True):
    if(schedules_):
        print(schedules_)
        schedule2 = schedules_.pop(0)
        print("schedule2", schedule2)
        service_id = schedule2["service_id"]
        request_ = schedule2["request"]
        # print("schedule2", schedule2)
        sch.StartSchedulling(request_,service_id)
    

sch.stop_all_started_at_their_Stop_time()
# t2 = threading.Thread(target=dumping_thread) 
# t2.start()
# app.run(debug=False,host="0.0.0.0",port=int(Myport)) 