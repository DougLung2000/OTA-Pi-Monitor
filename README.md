The OTA-Pi-Monitor is a collection of scripts and programs that will run on a Raspberry Pi or similar device to allow remote monitoring of a TV station. The systme provides a web site displaying real-time SNR/MER, signal level (dBm), continuity error count, and bit rate per PID once configured. A one-minute transport stream is captured every half hour and used to create MPEG-4 file for each configured stream. The video and audio are transcoded and saved with reduced frame rate and, for HD content, reduced resolution, to allow viewing with upload bit rates at or under 2 Mbps. TSDuck is used to provide an analysis of the recorded transport stream.  

These files were tested on a Raspberry Pi 5 with 4GB of RAM. It has also been tested on an Orange Pi 4 LTS and may work on other Debian Linux based single board computers if the required DVB firmware and utilities are available. This monitor is designed for use with the Hauppauge WinTV dualHD USB ATSC TV tuner but may be able to be modified to work with other tuners or DTV standard.

Here are the steps required to set up OTA-Pi-Monitor:

Install Raspberry Pi OS 64 bit "Lite" version with SSH enabled. See Raspberry Pi documentation for headless configuration. 
SSH to Raspberry Pi

Install these apt files: (sudo apt install [package name]):

  dvb-tools
  
  ffmpeg (will install huge number of files)
  
  nano (or other preferred text editor)
  
  w-scan
  
  git
  

Configure network (optional) using nmtui:

  Use settings to configure static IP address and set host name
  
  Also configure wi-fi if using, if not, disable it. Two interfaces can cause network issues.
  
  Verify last line in /etc/hosts file reflects the new host name - edit it if necessary
    (this will cause warnings when using sudo if not configured correctly)

Reboot if network changed

Set up folders:

    mkdir dtvdata
    
    cd dtvdata
    
Create venv [https://www.w3schools.com/python/python_virtualenv.asp]:

    python -m venv venv
    
Activate venv:

    source venv/bin/activate
    
Setup folders in venv:

    cd venv
    
    mkdir templates
    
    mkdir static
    
    mkdir static/js
    
Download the requirements.txt file from https://github.com/DougLung2000/OTA-Pi-Monitor/blob/main/src/PiOTA/requirements.txt and install in the virtual environment:

    scp requirements.txt tv@rpiota36.local://home/tv/dtvdata/venv/

Verify venv is active - prompt show show (venv) at start (i.e. (venv) tv@rpiota36:~/dtvdata/venv $)

Install required: Python files and dependencies:

    pip install -r requirements.txt

virtual environment is no longer needed the rest of the update

    deactivate

Return to home directory to clone files from github

    cd ~

    git clone https://github.com/DougLung2000/OTA-Pi-Monitor.git

Change to github download to complete initial installation

    cd OTA-Pi-Monitor/src/PiOTA/

    cp *.sh ~/dtvdata/

    chmod 755 ~/dtvdata/*.sh

    cp channels.zap ~/dtvdata/

    cp sigdata.py ~/dtvdata/venv/

    cp -R static/* ~/dtvdata/venv/static/

    cp -R templates/* ~/dtvdata/venv/templates/

    sudo dpkg -i tsduck_3.37-3636.debian12_arm64.deb

    sudo cp systemd/* /etc/systemd/system/

System is now set up with default configuration

    cd ~/dtvdata

Test tuner:

    sh ./sigdata3.sh
    
        Should show signal data if a channel 36 is present otherwise signal level only - press CTRL-C to exit
   
        Ignore "Command inversion" error
        
        If "tuning to 605000000 Hz" and signal levels are not displayed check tuner connection
        
    sh ./tscapproc.sh
    
        This will create the analyze.txt file and save captures from the program streams
        
If tuner works, start services:

    sudo systemctl start tscapproc.service

    sudo systemctl start gunisigdata.service

    sudo systemctl start tunertest.service

Next step is to create update files to match the channel you are monitoring

Files to be edited:

    channels.zap
    
    sigdata3.sh
    
    tscapproc.sh

Scan for channels using w_scan:
    
    w_scan -f a -c US -X > channels.zap

Make compatible with dvbv5 programs:

    sed -i 's/VSB_8/8VSB/g' channels.zap

Modifications: sigdata3.sh:

In the 13th lne change 'KMEB-HD' to the program channel name in the channel to be monitored. Any of the program names will work, but be sure to include any trailing spaces.

Modifications: tscapproc.sh:

In the 5th line change "KMEB-HD" to a program channel name on the channel you are monitoring. Any of the program names will work, but be sure to include any trailing spaces.The file names for the video samples should also be changed. I used the callsign and the program number but that is not critical. Note that these program names will also have to be changed in the index.html file in the templates directory. Also update the video size to match the settings in ffmpeg. The "-p map:3" refers to program number 3. These will need to be modified to match the program numbers in the channel being monitored. Additional lines can be added to monitor more than three program streams. Refer to ffmpeg documentation for details on the command line options.

Test modifications to scripts:

    sh ./sigdata3.sh
    
        Should show signal data and PIDs for the desired channel
        
        Ignore "Command inversion" error
    
    sh ./tscapproc.sh
    
        Should these files in dtvdata/venv/static:
        
            *.mp4 (video files for the streams configured in tscapproc.sh)
            
            analyze.txt (transport stream analysis for the configured channel)


Modifications: venv/templates/index.html

Replace 'K36OZ' with the callsign or other desired name of the channel being monitored

Change the text and links to the transport stream files generated by ffmpeg. The file names will be the ones you used in tscapproc.sh and be must match the .mp4 filenames in the venv/static/ directory.

Once modifications are completed, run:

    sudo systemctl restart tscapproc.service
    
    sudo systemctl restart gunisigdata.service
    
    sudo systemctl restart tunertest.service

Verify everything looks good. Once complete, to have the programs start on boot or reboot, run:

    sudo systemctl enable tscapproc.service
    
    sudo systemctl enable gunisigdata.service
    
    sudo systemctl enable tunertest.service

Reboot to verify systemd files are working
