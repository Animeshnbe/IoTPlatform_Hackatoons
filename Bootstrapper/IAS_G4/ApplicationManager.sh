printf "\n\n"
printf \"********************************************************\"; \
echo ---------------------- ApplicationManager -------------------------; \
printf \"********************************************************\"; \
echo "Deploying ApplicationManager.........."
printf "\n\n"

path="./ApplicationManager"
cd ${path}
echo $1 | sudo -S docker build . -t applicationmanager:latest;
echo $1 | sudo -S docker run applicationmanager

