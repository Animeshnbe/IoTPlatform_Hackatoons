printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- NodeManager -------------------------; \
printf \"********************************************************\"; \
echo "Deploying NodeManager.........."
printf "\n\n"

path="./NodeManager"
cd ${path}
echo $1 | sudo -S docker build . -t nodemanager:latest;
echo $1 | sudo -S docker run nodemanager

