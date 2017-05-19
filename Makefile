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

.PHONY: require-root install install-pkg install-hostapd install-doccam add-adafruit-repo enable-sudo-passwd clean

default:: ; @echo "Run 'sudo make install' to set up the software"

# set up software
install:: require-root install-pkg install-hostapd install-doccam
	# misc config
	# apache2
	ln -sf /etc/apache2/mods-available/cgi.load /etc/apache2/mods-enabled/
	# dnsmasq
	install -m 644 config/dnsmasq-doccam.conf /etc/dnsmasq.d/
	update-rc.d dnsmasq enable

	# disable screen blanking
	if ! grep -Fq "xserver-command=X -s 0 -dpms" /etc/lightdm/lightdm.conf; then \
	  echo "\n[SeatDefaults]\nxserver-command=X -s 0 -dpms" >> \
	    /etc/lightdm/lightdm.conf; \
	fi

	# require the user to enter the password to use sudo
	make enable-sudo-passwd

install-hostapd:: require-root install
	if [ ! -d install/RTL8188-hostapd/ ]; then \
	  git clone https://github.com/jenssegers/RTL8188-hostapd \
	    install/RTL8188-hostapd; \
	fi
	make -C install/RTL8188-hostapd/hostapd
	make -C install/RTL8188-hostapd/hostapd install

	install -m 644 config/hostapd.conf /etc/hostapd/
	install -m 644 config/interfaces /etc/network/

	update-rc.d hostapd defaults
	update-rc.d hostapd enable

# doccam source files
files-py = src/python/doccam-core src/python/doccam-gui src/python/doccam-gui-watchdog
files-py-mod = src/python/doccam/__init__.py src/python/doccam/cgihelper.py src/python/doccam/comm.py
files-cgi = src/cgi/config.py src/cgi/picture.py
files-html = src/html/about.html src/html/control.html src/html/index.html \
src/html/load-placeholder.png src/html/scripts.js src/html/style.css

install-doccam: require-root install $(files-py) $(files-py-mod) $(files-cgi) $(files-html) src/sh/doccam-core
	install -m 755 $(files-py) /usr/local/bin/
	mkdir -p /usr/local/lib/python2.7/dist-packages/doccam/
	install -m 755 $(files-py-mod) /usr/local/lib/python2.7/dist-packages/doccam/
	install -m 555 -o www-data -g www-data $(files-cgi) /usr/lib/cgi-bin/
	install -m 755 src/sh/doccam-core /etc/init.d/

	install -m 444 $(files-html) /var/www/html/

	update-rc.d doccam-core defaults
	update-rc.d doccam-core enable

	# enable gui autostart
	echo "#!/bin/bash\nsudo doccam-gui-watchdog" > /home/pi/.xsession

install-pkg:: require-root install add-adafruit-repo
	# create a new install/pkg file (the condition below will be satisfied)
	if [ ! -f install/pkg ]; then mkdir -p install; touch -d @0 install/pkg ; fi

	# if the install/pkg file is modified before the current time, update the packages
	if [ "$$(date +%s)" -ge "$$(stat -c %Y install/pkg)" ]; then \
	  echo "Updating packages"; \
	  apt-get update; \
	  echo "y\n" | apt-get dist-upgrade; \
	  apt-get -y install python-picamera python-pil python-tk \
	  adafruit-pitft-helper raspberrypi-bootloader raspberrypi-kernel \
	  xserver-xorg xinit xserver-xorg-video-fbdev lightdm apache2 dnsmasq git; \
		\
		if ! grep -Fq "adafruit-pitft-helper" /boot/config.txt; then \
		  echo "n\nn\n" | adafruit-pitft-helper -t 22; \
		fi; \
		\
	  # set the modification time of install/pkg one day in the future \
		touch -d @$$(($$(date +%s) + 24 * 60 * 60)) install/pkg; \
	else \
	  echo "Not updating packages"; fi

add-adafruit-repo:: require-root
	@# original from https://apt.adafruit.com/add-pin, modified
	if ! grep -Fq "adafruit" /etc/apt/sources.list; then \
	  # add apt repo to sources.list \
	  if grep -q "8.0" "/etc/debian_version"; then \
	    echo "deb http://apt.adafruit.com/raspbian/ jessie main" >> \
	      /etc/apt/sources.list; \
	  else \
	    echo "deb http://apt.adafruit.com/raspbian/ wheezy main" >> \
	      /etc/apt/sources.list; \
	  fi; \
	  wget -O - -q https://apt.adafruit.com/apt.adafruit.com.gpg.key | \
	    apt-key add -; \
	fi

	if [ ! -f /etc/apt/preferences.d/adafruit ]; then \
	  echo "Package: *\nPin: origin \"apt.adafruit.com\"\nPin-Priority: 1001" > \
	    /etc/apt/preferences.d/adafruit; \
	fi

require-root::
	@if ! [ $$(id -u) = 0 ]; then \
	echo "This target must be run as root!"; \
	exit 1; fi

enable-sudo-passwd:: require-root
	install -m 400 config/040_doccam /etc/sudoers.d/
	if [ -f /etc/sudoers.d/010_pi-nopasswd ]; then \
	  mv /etc/sudoers.d/010_pi-nopasswd /etc/sudoers.d/010_pi-nopasswd~; fi
	@echo "You can no longer use sudo without a password; to revert this change remove the trailing tilde from the file named /etc/sudoers.d/010_pi-nopasswd~"

clean:
	-rm -rf install/
