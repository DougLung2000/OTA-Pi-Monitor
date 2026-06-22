### The OTA-Pi-Monitor is a collection of scripts and programs that will run on a Raspberry Pi or similar device to allow remote monitoring of a TV station.

The system provides a web site displaying real-time SNR/MER, signal level (dBm), continuity error count, and bit rate per PID once configured. A one-minute transport stream is captured every half hour and used to create MPEG-4 file for each configured stream. The video and audio are transcoded and saved with reduced frame rate and, for HD content, reduced resolution, to allow viewing with upload bit rates at or under 2 Mbps. TSDuck is used to provide an analysis of the recorded transport stream.  

These files were tested on a Raspberry Pi 5 with 4GB of RAM. It has also been tested on an Orange Pi 4 LTS and may work on other Debian Linux based single board computers if the required DVB firmware and utilities are available. This monitor is designed for use with the Hauppauge WinTV dualHD USB ATSC TV tuner but may be able to be modified to work with other tuners or DTV standard.

#### Here are the steps required to set up OTA-Pi-Monitor:

Install Raspberry Pi OS 64 bit "Lite" version with SSH enabled. See Raspberry Pi documentation for headless configuration.  SSH to Raspberry Pi

##### Install these apt files: (sudo apt install [package name]):

`  dvb-tools`

`  ffmpeg (will install huge number of files)`

`  nano (or other preferred text editor)`

`  w-scan`

`  git`

##### Configure network (optional) using nmtui:

  Use settings to configure static IP address and set host name

  Also configure wi-fi if using, if not, disable it. Two interfaces can cause network issues.

  Verify last line in /etc/hosts file reflects the new host name - edit it if necessary
    (this will cause warnings when using sudo if not configured correctly)

##### Reboot if network changed

##### Set up folders:

    mkdir dtvdata
    
    cd dtvdata

##### Create venv [https://www.w3schools.com/python/python_virtualenv.asp]:

    python -m venv venv

##### Activate venv:

    source venv/bin/activate

##### Setup folders in venv:

    cd venv
    
    mkdir templates
    
    mkdir static
    
    mkdir static/js

##### Install required: Python files and dependencies:

While in the venv directory, download the requirements.txt file:

    https://github.com/DougLung2000/OTA-Pi-Monitor/raw/refs/heads/main/src/PiOTA/requirements.txt

Verify venv is active - prompt should show (venv) at start (i.e. (venv) tv@rpiota36:~/dtvdata/venv $)

    pip install -r requirements.txt

virtual environment is no longer needed the rest of the update

    deactivate

##### Return to home directory to clone files from github

    cd ~
    
    git clone https://github.com/DougLung2000/OTA-Pi-Monitor.git

##### Change to github download directory to complete initial installation

    cd OTA-Pi-Monitor/src/PiOTA/
    
    cp *.sh ~/dtvdata/
    
    chmod 755 ~/dtvdata/*.sh
    
    cp channels.zap ~/dtvdata/
    
    cp sigdata.py ~/dtvdata/venv/
    
    cp -R static/* ~/dtvdata/venv/static/
    
    cp -R templates/* ~/dtvdata/venv/templates/
    
    sudo dpkg -i tsduck_3.37-3636.debian12_arm64.deb
    
    sudo cp systemd/* /etc/systemd/system/

### System is now set up with default configuration

    cd ~/dtvdata

##### Test tuner:

```
sh ./sigdata3.sh
```

Should show signal data if a channel 36 is present otherwise signal level only - press CTRL-C to exit

Ignore "Command inversion" error
If "tuning to 605000000 Hz" and signal levels are not displayed check tuner connection and rerun script to verify the tuner is connected. 

```
`sh ./tscapproc.sh`
```

This will create the analysis.txt file and save captures from the program streams

##### If tuner works, start services:

    sudo systemctl daemon-reload
    
    sudo systemctl start tscapproc.service
    
    sudo systemctl start gunisigdata.service
    
    sudo systemctl start tunertest.service
    
##### Use browser to verify web server is working - ###.###.###.### is local IP address of Raspberry Pi

    http://###.###.###.###:8088
   

#### The following files must be updated to match the channel being monitored

    channels.zap
    
    sigdata3.sh
    
    tscapproc.sh

    sigdata-guni2.py # to add or subtract PID bit rate displays

##### Scan for channels using w_scan:

    w_scan -f a -c US -X > channels.zap

##### Make compatible with dvbv5 programs:

    sed -i 's/VSB_8/8VSB/g' channels.zap

##### Modifications: sigdata3.sh:

In the 13th lne change 'KMEB-HD' to the program channel name in the channel to be monitored. Any of the program names will work, but be sure to include any trailing spaces.

##### Modifications: tscapproc.sh:

In the 5th line change "KMEB-HD" to a program channel name on the channel you are monitoring. Any of the program names will work, but be sure to include any trailing spaces.The file names for the video samples should also be changed. I used the callsign and the program number but that is not critical. Note that these program names will also have to be changed in the index.html file in the templates directory. Also update the video size to match the settings in ffmpeg. The "-p map:3" refers to program number 3. These will need to be modified to match the program numbers in the channel being monitored. Additional lines can be added to monitor more than three program streams. Refer to ffmpeg documentation for details on the command line options.

##### Test modifications to scripts:

    sh ./sigdata3.sh

Output should show signal data  and PIDs for the desired station

If signal data and PIDs are not displaced or are for the wrong station, check sigdata3.sh configuration. 

Ignore "Command inversion" error

```
sh ./tscapproc.sh
```

##### Verify these files are present in the *dtvdata/venv/static* directory:

*.mp4 (video files for the streams configured in tascapproc.sh)

analyze.txt (transport stream analysis for the configured channel)

##### Modifications: venv/templates/index.html

Replace 'K36OZ' with the callsign or other desired name of the channel being monitored

Change the text and links to the transport stream files generated by ffmpeg. The file names will be the ones you used in tscapproc.sh and be must match the .mp4 filenames in the venv/static/ directory.

##### Modifications: venv/sigdata-guni2.py

The "SignalDataService" function in this script provides the real-time data to the web page. The default configuration will display bit rates for video PIDs decimal 49, 65, and 81. To remove a PID from the bit rate display, comment out all lines associated with it. Other PIDs can be added using the same format.

The locations that need to be changed to add or remove PIDs are in the variable declarations (pid49_rate = '') at the start of the function, in the "if" statements that look for the PID number in the data stream, and in the "SignalData =" statement that provides the formatted real time data to the web page. In the "if" statements looking for the PID bit rate data, the spaces before and after the PID number are important to ensure only the line with the PID data is returned, not other lines with the PID number embedded in a bit rate or other value. 

##### Once modifications are completed, run:

    sudo systemctl daemon-reload
    
    sudo systemctl restart tscapproc.service
    
    sudo systemctl restart gunisigdata.service
    
    sudo systemctl restart tunertest.service

Verify the program is working correctly.. 

##### Once complete, to have the programs start on boot or reboot, run:

    sudo systemctl enable tscapproc.service


    
    sudo systemctl enable gunisigdata.service
    
    sudo systemctl enable tunertest.service

##### Reboot to verify systemd files are working
#### Web page display:
<img width="559" height="965" alt="image" src="https://github.com/user-attachments/assets/b494260f-ef69-4782-a1c3-f00717ee7da1" />
