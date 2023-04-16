printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- ActionManager -------------------------; \
printf \"********************************************************\"; \
echo "Deploying ActionManager.........."
printf "\n\n"

path="./ActionManager"
cd ${path}
echo $1 | sudo -S docker build . -t actionmanager:latest;
echo $1 | sudo -S docker run actionmanager

