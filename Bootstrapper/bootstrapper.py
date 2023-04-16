import os
import time

pswd="1234"

#files=["install.sh", "Scheduler.sh", "Monitoring.sh", "ApplicationManager.sh", "ActionManager.sh", "Deployer.sh", "FaultTolerance.sh", #"NodeManager.sh", "SensorRegistry"]

files=["Authentication.sh","Scheduler.sh"]

print("Installing prerequisites.....\n")

# os.system(f"echo {pswd} | sudo -S scp -i ./IAS_G4/ias_key.pem ./IAS_G4.zip anm8@20.193.144.28:/home/anm8")

os.system(f"gnome-terminal --command=\"bash -c 'cd IAS_G4; echo {pswd} | sudo -S bash install.sh {pswd}; echo  ; exec bash'\"")

time.sleep(20)

for i in files:
    os.system(f"gnome-terminal --command=\"bash -c 'cd IAS_G4; echo {pswd} | sudo -S bash {i} {pswd}; echo  ; exec bash'\"")
