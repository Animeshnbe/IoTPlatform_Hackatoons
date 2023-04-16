printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- Monitoring -------------------------; \
printf \"********************************************************\"; \
echo "Deploying Monitoring.........."
printf "\n\n"

path="./Monitoring"
cd ${path}
echo $1 | sudo -S docker build . -t monitoring:latest;
echo $1 | sudo -S docker run monitoring

