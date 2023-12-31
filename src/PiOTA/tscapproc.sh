#!/bin/bash
# Stop any earlier dvr capturees
killall cat
# Copy the output from adapter0's dvr0 to a file
cat /dev/dvb/adapter0/dvr0 >| venv/static/K36OZ.ts & dvbv5-zap -I zap -c channels.zap "KMEB-HD" -t 60 -P -r
# Stop the dvr capture
killall cat
# Transcode HD Video - reduce resolution to 960x540
rm -f venv/static/K36OZ*.mp4
ffmpeg -i venv/static/K36OZ.ts -map p:3 -c:a aac -b:a 96K -c:v h264 -b:v 1M -s 960x540 -r 15 venv/static/K36OZ-3-540.mp4
# Transcode SD Video - no change in resolution
ffmpeg -i venv/static/K36OZ.ts -map p:4 -c:a aac -b:a 96K -c:v h264 -b:v 600K -r 15 venv/static/K36OZ-4-480.mp4
ffmpeg -i venv/static/K36OZ.ts -map p:5 -c:a aac -b:a 96K -c:v h264 -b:v 600K -r 15 venv/static/K36OZ-5-480.mp4
# Analyze transport stream
tsanalyze --usa venv/static/K36OZ.ts > venv/static/analysis.txt