#!/bin/bash
echo "Installing packages required for OTA Pi Monitor - This may take a while"
echo "Enter system password if requested to install system files"
sudo apt install dvb-tools ffmpeg nano w-scan
mkdir ~/dtvdata
python –m venv ~/dtvdata/venv
cp *.sh ~/dtvdata/
chmod 755 ~/dtvdata/*.sh
cp channels.zap ~/dtvdata/
cp sigdata-guni2.py ~/dtvdata/venv/
cp requirements.txt ~/dtvdata/venv/
cp -R static ~/dtvdata/venv/
cp -R templates ~/dtvdata/venv/
sudo dpkg -i tsduck_3.37-3636.debian12_arm64.deb
sudo cp w_scan2 /usr/local/bin
sudo cp systemd/* /etc/systemd/system/
cd ~/dtvdata/venv
/home/tv/dtvdata/venv/bin/pip3 install -r requirements.txt
echo "If no errors occurred during installation, connect tuner"
echo "and antenna to allow scanning channels."
