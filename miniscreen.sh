#!/bin/bash
# NobleProg Tech Ltd 2025 all rights reserved
# NobleProg Tech Ltd is registered in SAR Hong Kong
# This software is copyrighted
# To purchuse hardware of ddminiscreen visit www.dadesktop.com and ebay site
# ddsupport+ddminiscreen@nobleprog.com


dpkg -l python3-serial > /dev/null || apt install -y python3-serial python3-pil python3-psutil
dpkg -l python3-pil  > /dev/null || apt install -y  python3-pil
dpkg -l python3-psutil  > /dev/null || apt install -y python3-psutil
dpkg -l fonts-dejavu-core > /dev/null || apt install -y fonts-dejavu-core
[ -f /usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf ] ||  apt install -y fonts-dejavu-core
while true; do
    ./miniscreen.py
    sleep 4
done