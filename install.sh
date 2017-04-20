#!/bin/bash

# Raspberry Pi document camera
# Copyright (C) 2017  Nico Heitmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

sudo bash << EOF
# taken from https://apt.adafruit.com/add-pin
if grep -Fq "adafruit" /etc/apt/sources.list; then
  echo "adafruit repo already added to apt sources"
else
  # add apt repo to sources.list
  if grep -q "8.0" "/etc/debian_version"; then
    echo "deb http://apt.adafruit.com/raspbian/ jessie main" >> /etc/apt/sources.list
  else
    echo "deb http://apt.adafruit.com/raspbian/ wheezy main" >> /etc/apt/sources.list
  fi

  # import repo key
  wget -O - -q https://apt.adafruit.com/apt.adafruit.com.gpg.key | apt-key add -
fi

# pin apt.adafruit.com origin for anything installed there:
if [ ! -f /etc/apt/preferences.d/adafruit ]; then
  echo "pinning apt.adafruit.com origin"
  echo "edit /etc/apt/preferences.d/adafruit to change"
  echo -e "Package: *\nPin: origin \"apt.adafruit.com\"\nPin-Priority: 1001" > /etc/apt/preferences.d/adafruit
else
  echo "/etc/apt/preferences.d/adafruit already exists - leaving alone"
fi
EOF

# Update package database
sudo apt-get update

# Update and install required packages
echo "y\n" | sudo apt-get upgrade
sudo apt-get -y install raspberrypi-bootloader adafruit-pitft-helper raspberrypi-kernel python-picamera python-pil python-tk xserver-xorg xinit xserver-xorg-video-fbdev apache2 dnsmasq lightdm #git

# install modified hostapd from source
git clone https://github.com/jenssegers/RTL8188-hostapd
cd RTL8188-hostapd/hostapd/
make
sudo make install

cd ../..

# config
sudo ln -s /etc/apache2/mods-available/cgi.load /etc/apache2/mods-enabled/

sudo cp config/interfaces /etc/network/
sudo cp config/hostapd.conf /etc/hostapd/
sudo cp config/dnsmasq-doccam.conf /etc/dnsmasq.d/

# pitft config; chooses:
# 1) not to show console output on the pitft on startup
# 2) not to use GPIO #23 as shutdown
echo -e "n\nn\n" | sudo adafruit-pitft-helper -t 22

sudo chmod 644 /etc/network/interfaces /etc/hostapd/hostapd.conf /etc/dnsmasq.d/dnsmasq-doccam.conf

# disable screen blanking
# from https://raspberrypi.stackexchange.com/a/2103
echo -e "\n[SeatDefaults]\nxserver-command=X -s 0 -dpms" >> /etc/lightdm/lightdm.conf

# enable daemons
sudo update-rc.d hostapd defaults
sudo update-rc.d hostapd enable
sudo update-rc.d dnsmasq enable

# doccam source
sudo cp src/html/* /var/www/html/
sudo chmod 444 /var/www/html/*

sudo cp src/cgi/* /usr/lib/cgi-bin/
sudo chmod 555 /usr/lib/cgi-bin/*

sudo chown www-data /var/www/html/* /usr/lib/cgi-bin/*
sudo chgrp www-data /var/www/html/* /usr/lib/cgi-bin/*


# force sudo to be used with a password
sudo mv /etc/sudoers.d/010_pi-nopasswd /etc/sudoers.d/010_pi-nopasswd~
echo "You can no longer use sudo without a password; to revert this change remove the trailing tilde from the file name /etc/sudoers.d/010_pi-nopasswd~"
