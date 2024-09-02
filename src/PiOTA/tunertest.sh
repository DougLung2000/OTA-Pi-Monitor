#!/bin/bash
if journalctl -b -S today | grep "writing to i2c device at 0x1c failed (error=-5)";
then
  echo "Tuner i2c write error"
  sudo reboot
else
  echo "No tuner errors found"
fi
