#!/bin/bash

echo "deb http://ftp.de.debian.org/debian sid main contrib non-free" >> /etc/apt/sources.list

apt-get update -y
apt-get install -y docker.io

# remove APT line
sed -i '/.*sid main contrib non-free/d' /etc/apt/sources.list

apt-get update -y

exit
