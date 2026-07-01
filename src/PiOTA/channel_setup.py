# Script to scan for channels, set up transport stream capture, and grab a transport stream

import subprocess

import os
from pathlib import Path
def scan_channels():
    try:
        print("This may take several minutes. If scan is very slow, CTRL-C to kill script, unplug and replug in the USB tuner, and try again.")
        command = "w_scan2 -c US -f a -X > channels.zap"
        subprocess.run(command, shell=True)
        print("\n\n")
        result = "Success"
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        result = "Scan failed"
        exit()
    return

def load_channels():
    try:
#        print("Changing VSB_8 to 8VSB")
        command = "sed -i 's/VSB_8/8VSB/g' channels.zap"
        subprocess.run(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        result = "Scan failed"
        exit()
    channel_file = "channels.zap"
    channel_list = []
    try:
        with open(channel_file, mode='r') as file:
            for line in file:
#                print(line.rstrip('\n'))
                channel_list.append(line.rstrip('\n'))
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        result = "Scan failed"
        exit()
    return(channel_list)

def channel2frequency():
    channel_frequency = {
        "3":"63000000",
"2":"57000000",
"4":"69000000",
"5":"79000000",
"6":"85000000",
"7":"177000000",
"8":"183000000",
"9":"189000000",
"10":"195000000",
"11":"201000000",
"12":"207000000",
"13":"213000000",
"14":"473000000",
"15":"479000000",
"16":"485000000",
"17":"491000000",
"18":"497000000",
"19":"503000000",
"20":"509000000",
"21":"515000000",
"22":"521000000",
"23":"527000000",
"24":"533000000",
"25":"539000000",
"26":"545000000",
"27":"551000000",
"28":"557000000",
"29":"863000000",
"30":"569000000",
"31":"575000000",
"32":"581000000",
"33":"587000000",
"34":"593000000",
"35":"599000000",
"36":"605000000"}
    return(channel_frequency)
    
def frequency2channel():
    frequency_channel = {
        "57000000":"2",
"63000000":"3",
"69000000":"4",
"79000000":"5",
"85000000":"6",
"177000000":"7",
"183000000":"8",
"189000000":"9",
"195000000":"10",
"201000000":"11",
"207000000":"12",
"213000000":"13",
"473000000":"14",
"479000000":"15",
"485000000":"16",
"491000000":"17",
"497000000":"18",
"503000000":"19",
"509000000":"20",
"515000000":"21",
"521000000":"22",
"527000000":"23",
"533000000":"24",
"539000000":"25",
"545000000":"26",
"551000000":"27",
"557000000":"28",
"863000000":"29",
"569000000":"30",
"575000000":"31",
"581000000":"32",
"587000000":"33",
"593000000":"34",
"599000000":"35",
"605000000":"36"}
    return(frequency_channel)

def find_channel(channel_frequency):
    frequency = ""
    while frequency == "":
        print("Enter RF (transmit) channel number or center frequency in Hertz to monitor:")
        chan = input()
        if len(chan) < 3 :
            try:
                frequency = channel_frequency[chan]
#                print("frequency for channel ",chan,": ",frequency)
            except:
                print("RF channel ",chan," is not valid - must be in the rnage 2 to 36")
        elif len(chan) > 7 & len(chan) < 10:
            print("Center frequency {chan} Hz entered")
            try:
                frequency2 = chan
                chan = frequency_channel[frequency2]
                frequency = channel_frequency[chan]
#                print("frequency for channel ",chan,": ",frequency2)
            except:
                print("RF frequency entered is not valid - must be s U.S. TV center frequency in Hertz")
        else:
            print("Channel or center frequency entered is not valid")
    return(frequency)

def find_station(frequency,channel_list):
    station = ""
    frequency = ":" + frequency
    for item in channel_list:
        if station == "" and frequency in item:
            station = item
    if station == "":
        station = "No station found"
    return(station)

def create_sigdata3(station):
    station_detail = []
    station_detail = station.split(":")
    station_name = '"' + station_detail[0] + '"'
    script = "#!/bin/bash\n\nint_handler()\n{\n    echo 'interrupted'\n"
    script = script +"    # Kill the parent process of the script.\n"
    script = script +"    kill $PPID\n"
    script = script +"    exit 1\n}\n"
    script = script +"dtvdata()\n{\n"
    script = script +"    trap 'int_handler' INT\n"
    script = script +"    timeout --foreground 300 dvbv5-zap -a 1 -m -I ZAP -c ~/dtvdata/channels.zap -C US "+station_name+"\n}\n\n"
    script = script +"while true; do\n"
    script = script +"    dtvdata\n"
    script = script +"    sleep 15\ndone\n"
    return(script)

def create_tscapproc_1(station):
    station_detail = []
    station_detail = station.split(":")
    station_name = '"' + station_detail[0] + '"'
    capture_command = "cat /dev/dvb/adapter0/dvr0 >| venv/static/ota.ts & dvbv5-zap -I zap -c channels.zap " + station_name + " -t 60 -P -r"
    
    script = "#!/bin/bash\n"
    script = script + "# Stop any earlier dvr captures\n"
    script = script + "killall cat\n"
    script = script + "# Copy the output from adapter0's dvr0 to a file\n"
    script = script + capture_command + "\n"
    script = script + "# Stop the dvr capture\n"
    script = script + "killall cat\n"
    return(script)
                      
def save_script(script,script_name):
    with open(script_name, "w") as script_file :
        script_file.close()
    with open(script_name, "a") as script_file :
        script_file.write(script)
    os.chmod(script_name, 0o755)
    return()

def record_ts_file():
    try:
        print("Recording a transport stream for additional analysis")
        command = "sh ./tscapproc_1.sh"
        subprocess.run(command, shell=True)
        result = "Success"
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        result = "Scan failed"
        exit()
    return(result)

def analyze_ts():
    try:
        print("Extracting data from ota.ts file for analysis")
        command = ["ffprobe","/home/tv/dtvdata/venv/static/ota.ts","-show_format","-output_format","csv"]
        with open("otadata.txt", "w") as f:
            subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)
        f.close()
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
    print("Loading otadata.txt for analysis")
    otadata = "otadata.txt"
    ts_data = {}
    with open(otadata, mode='r') as file:
        for line in file:
            if "Program" in line:
                Pgm_number = line.strip().split(' ')[1].strip()
                print("Program Number is:",Pgm_number)
                ts_data.setdefault(Pgm_number,[])
                video_data = []
                audio_data = []
            if " Video: " in line:
                video_PID = line.strip().split(":")[1]
                video_PID = video_PID.split("[")[1]
                video_PID = video_PID.split("]")[0]
                print("Video PID of Program",Pgm_number,"is",video_PID)
                video_size = line.strip().split(",")[3]
                video_size = video_size.split("[")[0].strip()
                print("Video size of Program",Pgm_number,"is",video_size)
                video_data = [video_PID,video_size]
            if " Audio: " in line:
                audio_PID = line.strip().split(":")[1]
                audio_PID = audio_PID.split("[")[1]
                audio_PID = audio_PID.split("]")[0]
                audio_type = line.strip().split(",")[2].strip()
                audio_rate = line.strip().split(",")[4].strip()
                print("Audio PID of Program",Pgm_number,"is",audio_PID,"type",audio_type,"at",audio_rate)
                if audio_data == []:
                    audio_data=[audio_PID,audio_type]
                ts_data[Pgm_number].append([video_data,audio_data])
                
    return(ts_data)

def create_tscapproc_2(ts_data):
    # Get list of program numbers
    pgms = list(ts_data)
    # Create list with ffmpeg command for each program
    ffmpegCommand = "ffmpeg -i /home/tv/dtvdata/venv/static/ota.ts -map p:"
    VideoLocation = " venv/static/ota-"
    script = "rm -f venv/static/ota*.mp4\n"
    for item in pgms:
        Program_number = item
        pgm = ts_data.get(item)
        if "5.1" in pgm[0][1][1] :
            AudioFormat = " -c:a aac -b:a 96K -ac 2"
        else:
            AudioFormat = " -c:a aac -b:a 96K"
        if '480' in pgm[0][0][1] :
            VideoFormat = " -c:v h264 -b:v 600K -r 15"
            VideoType = "-480.mp4"
        else:
            VideoFormat = " -c:v h264 -b:v 1M -s 960x540 -r 15"
            VideoType = "-540.mp4"
        script = script + ffmpegCommand + Program_number + AudioFormat + VideoFormat + VideoLocation + Program_number + VideoType + "\n"
        print(script)
    script = script + "tsanalyze --usa venv/static/ota.ts > /home/tv/dtvdata/venv/static/analysis.txt"
    print(script)
    return(script)

def create_mp4_files():
    try:
        subprocess.run(["sh","./tscapproc_2.sh"])
    except:
        print("Unable to run tscapproc_2.sh. Exiting setup program.")
        print("Check tuner and antenna connection and try setup again.")
        exit()
    directory = Path("/home/tv/dtvdata/venv/static/")
    file_exists = any(directory.glob("*.mp4"))
    if file_exists:
        print("At least one mp4 file created. Setup will continue.")
    else:
        print("No mp4 files found. Setup will exit. Check tuner connection and try setup again.")
        exit()


def create_tscapproc():
    command = ["cat","/home/tv/dtvdata/tscapproc_1.sh","/home/tv/dtvdata/tscapproc_2.sh"]
    with open("/home/tv/dtvdata/tscapproc.sh", "w") as f:
            subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)
    f.close()
    subprocess.run(["chmod","755","tscapproc.sh"])
    return()


def replace_callsign(file):
    while True:
        callsign = input("Enter callsign to show on web page (max 12 alphanumeric characters): ")
        # Check conditions
        if len(callsign) <= 15:
            break
        else:
            print("Invalid input. Please ensure it is max 15 characters and only contains letters/numbers.")
    try:
        #print("Changing callsign on web page")
        command = "cp /home/tv/OTA-Pi-Monitor/src/PiOTA/index-start.html /home/tv/dtvdata/index-1.html"
        command = "sed -i 's/K36OZ/"+callsign+"/g' index-1.html"
        print(command)
        subprocess.run(command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        print("Changing label text on web page failed. Exiting setup.")
        print("Check that index-start.html is available in /home/tv/OTA-Pi-Monitor/src/PiOTA")
        exit()
    return()
     
def create_links(ts_data):
    # Get list of program numbers
    pgms = list(ts_data)
    script = ""
    # Create links for each program
    for item in pgms:
        Program_number = item
        pgm = ts_data.get(item)
        video_size = pgm[0][0][1].strip()
        if video_size.split("x")[1] != "480" :
                video_size = "960x540"
        video_width = video_size.split("x")[0]
        video_height = video_size.split("x")[1]
        script = script + f"<p>Program Stream {Program_number} MPEG4/AAC transcode to {video_size} at 15 fps</p>\n \
<video width='{video_width}' height='{video_height}' controls>\n"
        # Create text for <source>
        script = script + "<source src=\"{{url_for('static', filename='ota-"+Program_number+'-'+video_height+".mp4')}}\" type=\"video/mp4\">\n \
</video>\n\n"
    return(script)

def update_webpage():
    command = ["cat","/home/tv/dtvdata/index-1.html","/home/tv/dtvdata/index-2.html","/home/tv/dtvdata/index-3.html"]
    with open("/home/tv/dtvdata/venv/templates/index.html", "w") as f:
            subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)
    f.close()
    return()

def enable_systemd_units():
    try:
        command = "sudo systemctl enable tscapproc.timer gunisigdata.service tunertest.timer"
        subprocess.run(command, shell=True)
        print("INSTALLATION HAS COMPLETED")
        print("REBOOT RASPBERRY PI TO START MONITORING AND WEB SERVER")
        print("AFTER REBOOT, WEB SITE IS AT: http://[Raspberry Pi IP address]:0888")
        print("REBOOT NOW USING 'sudo reboot'")
    except:
        subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error message: {e.stderr}")
        print("Unable to start systemd services.")
        print("Try starting manually one by one and use systemctl status to identify the problem.")
    return()


scan_channels()
channel_list = load_channels()
#print(channel_list)
channel_frequency = channel2frequency()
frequency_channel = frequency2channel()
frequency = find_channel(channel_frequency)
print("\nfind_channel returned frequency: ",frequency)
station = find_station(frequency,channel_list)
print("Station data found: ",station,"\n\n")
script = create_sigdata3(station)
save_script(script,"sigdata3.sh")
print(script)
script = create_tscapproc_1(station)
save_script(script,"/home/tv/dtvdata/tscapproc_1.sh")
record_ts_file()
ts_data = analyze_ts()
script = create_tscapproc_2(ts_data)
save_script(script,"/home/tv/dtvdata/tscapproc_2.sh")
create_mp4_files()
create_tscapproc()
script = create_links(ts_data)
print(script)
save_script(script,"/home/tv/dtvdata/index-2.html")
replace_callsign("/home/tv/dtvdata/index-1.html")
update_webpage()
enable_systemd_units()

exit()

        
