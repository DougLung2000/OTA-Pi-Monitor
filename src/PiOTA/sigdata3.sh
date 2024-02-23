#!/bin/bash

int_handler()
{
    echo "Interrupted."
    # Kill the parent process of the script.
    kill $PPID
    exit 1
}
dtvdata()
{
    trap 'int_handler' INT
    timeout --foreground 300 dvbv5-zap -a 1 -m -I ZAP -c ~/dtvdata/channels.zap -C US 'KMEB-HD'
}

while true; do
    dtvdata
    sleep 15
done
