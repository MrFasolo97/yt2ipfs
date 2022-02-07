#!/usr/bin/env bash
sudo apt update
if ! command -v pip3 &> /dev/null
then
  sudo apt install python3-pip
fi

if ! command -v python3 &> /dev/null
then
  sudo apt install python3
fi

if ! command -v youtube-dl &> /dev/null
then
  sudo apt install youtube-dl
fi

sudo pip3 install -r requirements.txt

if ! [[ -f config.json ]]
then
  cp config_example.json config.json
  chmod 0600 config.json
else
  echo "Config file already there, skipping..."
fi
