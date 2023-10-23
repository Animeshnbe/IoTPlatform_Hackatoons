#!/bin/bash

pswd="1234"

echo ""
echo ""
echo ""
echo "**************************************************************************"
echo "*************************** INSTALLING DOCKER ****************************"
echo "**************************************************************************"
echo ""
echo ""
echo ""
# Update the package index
echo ${pswd} | sudo -S apt-get update

# Install packages to allow apt to use a repository over HTTPS
echo ${pswd} | sudo -S apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | echo ${pswd} | sudo -S gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository to APT sources
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | echo ${pswd} | sudo -S tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update the package index again
echo ${pswd} | sudo -S apt-get update

# Install the latest version of Docker
echo ${pswd} | sudo -S apt-get install -y docker-ce docker-ce-cli containerd.io

# Add the current user to the docker group to run docker without sudo
echo ${pswd} | sudo -S usermod -aG docker $USER

# Display the Docker version
docker --version
echo ""
echo ""
echo ""
echo "**************************************************************************"
echo "********************** DOCKER INSTALLED SUCCESSFULLY *********************"
echo "**************************************************************************"
echo ""
echo ""
echo ""
echo "**************************************************************************"
echo "************************ INSTALLING GNOME-TEMINAL ************************"
echo "**************************************************************************"
echo ""
echo ""
echo ""
# Update the package index
echo ${pswd} | sudo -S apt update

# Install the GNOME Terminal package
echo ${pswd} | sudo -S apt install gnome-terminal

# Verify the installation
gnome-terminal --version

echo ""
echo ""
echo ""
echo "**************************************************************************"
echo "********************** GNOME-TEMINAL INSTALLED SUCCESSFULLY **************"
echo "**************************************************************************"
echo ""
echo ""
echo ""
