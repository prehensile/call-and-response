##
# Set up a new Raspberry Pi OS installation for Canto.
#

# make sure package sources are up to date
sudo apt update

# install python3 and pip3
sudo apt install -y python3-pip

# install python neopixel dependencies
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

# install pygame & dependencies
sudo apt install -y python3-pygame

# install pillow & dependencies
sudo pip3 install pillow
sudo apt install -y libopenjp2-7 libtiff5

# copy alsa config for USB audio into place
sudo cp /boot/asound.conf /etc

# copy canto source into place
mkdir -p ~/src/canto
cp -R /boot/canto ~/src/canto/src

# install requirements from file
sudo pip3 install -r ~/src/canto/src/requirements.txt

