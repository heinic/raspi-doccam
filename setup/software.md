# Software Setup

Download [raspbian lite](https://www.raspberrypi.org/downloads/raspbian/)
and load it onto the SD card. Instructions can be found on the download page.

Start up the Raspberry Pi and log in with the user `pi` and the password
`raspberry`. Use `sudo raspi-config` and choose the following options:
- Expand the Filesystem
- If needed, update the language, keyboard layout and timezone
- Change the password  
  This password is only required for administration purposes
- Enable the camera
- Enable SSH

Run `ifconfig` and note down the ip address on eth0.

Reboot the Raspberry Pi (`sudo reboot`). The keyboard and monitor are no longer
required.

Connect to the Raspberry Pi via ssh and log in with your new password.

Now run `sudo apt-get update && sudo apt-get -y install git`.
Clone the source code repository of this project using
`git clone https://github.com/heinic/raspi-doccam`. Navigate to the newly
created folder with `cd raspi-doccam`.

Lastly, you need to run the installation: `sudo make install`
