#!/bin/bash
# NobleProg Tech Ltd 2025 all rights reserved
# NobleProg Tech Ltd is registered in SAR Hong Kong
# This software is copyrighted
# To purchuse hardware of ddminiscreen visit www.dadesktop.com and ebay site
# ddsupport+ddminiscreen@nobleprog.com


NAME=`basename "$PWD"`
SERVICE=${NAME}.service

[ -L /etc/systemd/system/$SERVICE ] && [ ! -e /etc/systemd/system/$SERVICE ]  &&    rm  /etc/systemd/system/$SERVICE

LINK="FALSE"
[ -L /etc/systemd/system/$SERVICE ] || { ln -fs `pwd`/$SERVICE /etc/systemd/system/ && LINK="TRUE"; }
[ $LINK  == "TRUE" ] &&  systemctl daemon-reload
systemctl -q is-enabled $SERVICE   ||  systemctl enable --now  $SERVICE
