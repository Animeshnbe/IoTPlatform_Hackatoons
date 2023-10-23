printf "\n\n"
printf \"********************************************************\n\"; \
echo ---------------------- Authentication -------------------------; \
printf \"********************************************************\"; \
echo "Deploying Authentication.........."
printf "\n\n"

path="./Authentication"
cd ${path}
echo $1 | sudo -S docker build . -t aut:latest;
echo $1 | sudo -S docker run aut

