printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- Scheduler -------------------------; \
printf \"********************************************************\"; \
echo "Deploying Scheduler.........."
printf "\n\n"

path="./Scheduler"
cd ${path}
echo $1 | sudo -S docker build . -t scheduler:latest;
echo $1 | sudo -S docker run scheduler

