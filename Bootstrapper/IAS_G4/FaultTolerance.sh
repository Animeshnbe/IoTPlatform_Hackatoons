printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- FaultTolerance -------------------------; \
printf \"********************************************************\"; \
echo "Deploying FaultTolerance.........."
printf "\n\n"

path="./FaultTolerance"
cd ${path}
echo $1 | sudo -S docker build . -t faulttolerance:latest;
echo $1 | sudo -S docker run faulttolerance

