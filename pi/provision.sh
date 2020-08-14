##
# Set up a new Raspberry Pi OS installation for Canto.
#

# make sure package sources are up to date
sudo apt update

# install python3 and pip3
sudo apt install python3-pip

# install python neopixel dependencies
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

# copy alsa config for USB audio into place
sudo cp /boot/asound.conf /etc


