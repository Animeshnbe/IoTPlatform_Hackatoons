** Always mkdir /flows in the machine attach /flows as volume to the container of both node red and workflow while running **

docker run -p8886:8886 -v node_red_data:/flows -v /home/anm8/services:/services --name workflow_manager workflow_manager