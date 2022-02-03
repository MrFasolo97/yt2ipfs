#!/usr/bin/env bash
if ! command -v pip3 &> /dev/null
then
  sudo apt update
  sudo apt install python3-pip
fi

if ! command -v python3 &> /dev/null
then
  sudo apt install python3
fi

sudo pip3 install -r requirements.txt

if ! file config.json &> /dev/null
then
  cp config_example.json config.json
  chmod 0600 config.json
else
  echo "Config file already there, skipping..."
fi
