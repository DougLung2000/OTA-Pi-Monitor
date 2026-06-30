### The OTA-Pi-Monitor is a collection of scripts and programs that will run on a Raspberry Pi or similar device to allow remote monitoring of a TV station.

The system provides a web site displaying real-time SNR/MER, signal level (dBm), continuity error count, and bit rate per PID once configured. A one-minute transport stream is captured every half hour and used to create MPEG-4 file for each configured stream. The video and audio are transcoded and saved with reduced frame rate and, for HD content, reduced resolution, to allow viewing with upload bit rates at or under 2 Mbps. TSDuck is used to provide an analysis of the recorded transport stream.  

These files were tested on a Raspberry Pi 5 with 4GB of RAM. It has also been tested on an Orange Pi 4 LTS and may work on other Debian Linux based single board computers if the required DVB firmware and utilities are available. This monitor is designed for use with the Hauppauge WinTV dualHD USB ATSC TV tuner but may be able to be modified to work with other tuners or DTV standard.

The USB driver in the Raspberry Pi may drop i2c packets. The tunertest.sh script detects this when monitoring and reboots the Pi if this happens but it is not running during configuration. During configuration, if the channel_setup.py script takes more than a few seconds to start scanning or more than a few seconds on each channel, USB tuner communication has likely failed. Abort the configuration with CTRL-C, unplug and replug the USB tuner, and rerun channel_setup.py or reboot the Raspberry Pi. Minimize the chances of this happening by using the USB 2.0 ports (black color) on the Raspberry Pi for the tuner. 

#### Here are the steps required to set up OTA-Pi-Monitor:

Install Raspberry Pi OS 64 bit "Lite" version with SSH enabled. See Raspberry Pi documentation for headless configuration. This configuration depends on a user name "tv". Any other user name will require modifying the scripts and file locations. SSH to Raspberry Pi to complete installation. Install any available updates:

    sudo apt update

    sudo apt upgrade
    
##### Configure network (optional) using nmtui:

  Use settings to configure static IP address and set host name

  Also configure wi-fi if using, if not, disable it. Two interfaces can cause network issues.

  Verify last line in /etc/hosts file reflects the new host name - edit it if necessary
    (this will cause warnings when using sudo if not configured correctly)

##### Reboot if network changed

##### Install git:

    sudo apt install git

##### Clone Github files:

    git clone https://github.com/DougLung2000/OTA-Pi-Monitor.git && cd OTA-Pi-Monitor/src/PiOTA

##### Run install script to create required directories, web server, and sample scripts (enter user password if requested):

    sh ./install-1st.sh

##### If script completes successfully, start web server and verify it works:
    
    sudo systemctl start gunisigdata.service && sudo systemctl status gunisigdata.service
    
##### Use browser to verify web server is working - ###.###.###.### is local IP address of Raspberry Pi

    http://###.###.###.###:8088
   
##### If web server displays default page (video and bit rate data will be missing), stop web server and change to dtvdata directory
    
    sudo systemctl stop gunisigdata.service
    
#### Run channel_setup.py to scan channels, create scripts to monitor and view transcoded video on the web page

    cd ~/dtvdata && python channel_setup.py

##### After script finished, reboot Raspberry Pi 

##### After rebooting, generate the transcoded video samples (if transport stream recording doesn't start, plug and unplug tuner)

    cd dtvdata && sh ./tscapproc.sh

##### After script finishes, verify ota.ts and mp4 files are present and not 0 bytes in ~/dtvdata/venv/static:

    ls -l venv/static/

##### If ota.ts and mp4 files are present:
    
    sudo systemctl start tscapproc.timerc && sudo systemctl start gunisigdata.service && sudo systemctl start tunertest.timer

##### Use browser to check web page at http:[Raspberry Pi IP address]:8088, if good, to have program start on reboot:

    sudo systemctl enable tscapproc.timer

    
    sudo systemctl enable gunisigdata.service

    
    sudo systemctl enable tunertest.timer

##### Reboot to verify systemd files are working and web server is working

##### Optional modifications to sigdata-guni2.py to add or remove PIDs for bit rate display

The "SignalDataService" function in this script provides the real-time data to the web page. The default configuration will display bit rates for video PIDs decimal 49, 65, and 81. To remove a PID from the bit rate display, comment out all lines associated with it. Other PIDs can be added using the same format.

The locations that need to be changed to add or remove PIDs are in the variable declarations (pid49_rate = '') at the start of the function, in the "if" statements that look for the PID number in the data stream, and in the "SignalData =" statement that provides the formatted real time data to the web page. In the "if" statements looking for the PID bit rate data, the spaces before and after the PID number are important to ensure only the line with the PID data is returned, not other lines with the PID number embedded in a bit rate or other value. 

If modifications fail, the sigdata-guni2.py file from Github is not modified during a normal install and can be used to replace a modified script that failed.

If there is significant interest in showing additional bit rates, I can look at adding creation of a modified sigdata-guni2.py with all video PIDs displayed to the channel_setup.py script. 

##### IMPORTANT: Once modifications are completed, reboot the Raspberry Pi

#### Web page display:
<img width="559" height="965" alt="image" src="https://github.com/user-attachments/assets/b494260f-ef69-4782-a1c3-f00717ee7da1" />
