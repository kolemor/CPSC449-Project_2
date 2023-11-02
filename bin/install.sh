#!/bin/bash

# Update package lists
sudo apt update

# Install sqlite3
sudo apt install --yes sqlite3

# Install ruby-foreman
sudo apt install -y ruby-foreman

# Install entr
sudo apt install -y entr

# ***** Block to install KrakenD *****
# Add the GPG key for the specified keyserver
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv 5DE6FD698AD6FDD2

# Add Krakend repository to sources list
sudo echo "deb https://repo.krakend.io/apt stable main" | sudo tee /etc/apt/sources.list.d/krakend.list

# Update package lists
sudo apt update

# Install KrakenD
sudo apt install -y krakend

# ***** Block to install REdis *****
# Update package lists
sudo apt update

# Install REdis 
sudo apt install --yes redis

# ***** Block to install AWS CLI *****
# Download the installer
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip the installer
unzip awscliv2.zip

# Install AWS CLI
sudo ./aws/install


# ***** Block to install DynamoDB *****
# Update package lists
sudo apt update

# Install JRE
sudo apt install --yes openjdk-19-jre-headless



# *************************************

# Install HTTPie for Terminal to work with REST APIs
sudo apt install -y httpie

# Install pip for Python 3
sudo apt install -y python3-pip

# Install required libaries for the project
pip3 install -r requirements.txt

# Print 'Installation Successful'
echo "\n\n"
echo "*****************************************"
echo "*        Installation Successful        *"
echo "*****************************************"
echo "To start the servers, run: 'sh run.sh'"
echo "\n" 