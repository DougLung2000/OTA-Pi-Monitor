# 2024-02-22
Moved tuner reset to the sigdata3.sh script and removed the 10 minute timeout from the sigdata.service, avoiding loss of the web site every 10 minutes. The user only notices a short pause in the update of the real-time data during the tuner reset, which is every 5 minutes (300 seconds) in the new sigdata3.sh script.  

# OTA-Pi-Monitor
Remotely monitor over-the-air digital TV transmissions with ARM SBCs

These files were used to build the OTA-Pi Monitor to receive TV translator K36OZ. They have been tested on an Orange Pi 4 LTS (4 GB RAM, 16 GB eMMC) and on a Raspberry Pi 5 (4 GB RAM, 32 GB micro-SD card) with the Hauppauge WinTV dualHD ATSC 1.0 tuner. 

The following programs must be installed. These are the package names for the Raspberry Pi OS (64-bit): virtualenv ffmpeg dvb-tools w-scan  

The program uses the tsduck "tsanalyze" program to create the detailed transport stream analysis. This program is not difficult to build from source (see https://github.com/tsduck/tsduck) if the features requiring extra libraries are not built. I have created a binary for the Raspberry Pi 5 OS (64-bit) - tsduck_3.37-3636.debian12_arm64.deb - which can be installed with "sudo dpkg -i tsduck_3.37-3636.debian12_arm64.deb". Verify it works after installation with "tsanalyze --version". If tsanalyze is NOT available, comment out all reference to it in tscapproc.sh. The Python script and index.html in templates will also have to be modified unless a "analysis.txt" file with some arbitrary text is placed in the static directory. It will be displayed below the videos. 

To install, create a "dtvdata" subdirectory in the home directory. The sigdata3.sh, channels.zap, and tscapproc.sh files go in this directory. Run "w_scan -fa -c US -X > channels.zap" to obtain a list of local channels after the USB tuner and antenna are connected. Edit the list to include only the program streams on the station to be monitored. A simple way to do this is to use grep and the channel center frequency (in Hz): "cat channels.zap | grep '557000000' > channel28.zap" is an example that will save all programs on 557000000 Hz (channel 28) to a new file. Verify the file has the correct programs and then copy it to channels.zap, the file name used in the script (overwriting the full list) The w_scan VSB_8 is not compatible with the dvbv5 tools so use "sed" to replace it: "sed -i 's/VSB_8/8VSB/g' channels.zap"

At this point, you can run the sigdata3.sh script to verify the tuner is working. Use CTRL-C to stop it. 

From the dtvdata directory, create a Python virtual environment called "venv" and activate it. Place the sigdata.py file in this directory and make the "templates" and "static" directories below it. Make a "js" directory in the static directory. Verify you are in the venv folder and the virtual environment is activated - the command prompt will show (venv). Install the required Python modules with "pip3 install flask-socketio" and "pip3 install gevent"

The tscapproc.sh file will need to be modified. In the 5th line change "KMEB-HD" to a program channel name on the channel you are monitoring. Any of the program names will work, but be sure to include any trailing spaces.The file names for the video samples should also be changed. I used the callsign and the program number but that is not critical. Note that these program names will also have to be changed in the index.html file in the templates directory. Also update the video size to match the settings in ffmpeg. The "-p map:3" refers to program number 3. These will need to be modified to match the program numbers in the channel being monitored. Additional lines can be added to monitor more than three program streams. Refer to ffmpeg documentation for details on the command line options.  

Once these changes have been made, run the tscapproc.sh script to generate the files for the static folder. 

The sigdata.py program can now be run from the virtual environment ("python3 sigdata.py"). The web page should be visible at the IP address of the Pi-OTA server (Raspberry Pi or Orange Pi) with the port number :8088 added to the IP address. The port number can be changed in the last line of the sigdata.py script. Edit the index.html file to change any headings or text as necessary. 

After verifying the program is running fine, copy the files in the systemd folder to "/etc/systemd/system/" and enable and start them using systemctl as sudo. The status of the program can be monitoring using the "systemctl status sigdata.service". See systemd documentation for more information on systemd and operation of the tscapproc.timer module that schedules when the video samples are recorded. 

If there are any questions, email me at dlung@transmitter.com
