printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- Deployer -------------------------; \
printf \"********************************************************\"; \
echo "Deploying Deployer.........."
printf "\n\n"

path="./Deployer"
cd ${path}
echo $1 | sudo -S docker build . -t deployer:latest;
echo $1 | sudo -S docker run deployer

