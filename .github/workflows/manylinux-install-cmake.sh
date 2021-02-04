#!/bin/bash

set -x
set -e

# Remove the ancient version of cmake
yum remove cmake -y

# Add in curl
yum install wget -y

yum install java-1.8.0-openjdk uuid uuid-devel libuuid libuuid-devel -y

# Download new cmake
wget https://github.com/Kitware/CMake/releases/download/v3.19.4/cmake-3.19.4-Linux-x86_64.sh -O /tmp/cmake.sh
chmod a+x /tmp/cmake.sh

# Install cmake into /usr
/tmp/cmake.sh --prefix=/usr --skip-license
