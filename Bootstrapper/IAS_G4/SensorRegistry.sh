printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- SensorRegistry -------------------------; \
printf \"********************************************************\"; \
echo "Deploying SensorRegistry.........."
printf "\n\n"

path="./SensorRegistry"
cd ${path}
echo $1 | sudo -S docker build . -t sensorregistry:latest;
echo $1 | sudo -S docker run sensorregistry

