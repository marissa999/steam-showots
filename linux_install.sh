#!/usr/bin/env bash

USER=$(whoami)
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

printf "Setting up script for $USER in path $SCRIPTPATH\n\n"

cd $SCRIPTPATH


printf "Creating venv: 'python -m venv'\n"
python -m venv $SCRIPTPATH
printf "venv created...\n\n"


printf "Active venv: 'source $SCRIPTPATH/bin/activate'\n"
source $SCRIPTPATH/bin/activate
printf "venv activated...\n\n"


printf "Installing all dependencies: '$SCRIPTPATH/bin/pip install -r $SCRIPTPATH/requirements.txt'\n"
$SCRIPTPATH/bin/pip install -r $SCRIPTPATH/requirements.txt
printf "Dependencies installed...\n\n"


printf "Setting up systemd user service...\n"
SYSTEMD_SERVICE_CONTENT=$(cat <<EOF
[Unit]
Description=steam-showots
After=network.target

[Service]
Type=simple
Restart=on-failure
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/bin/python main.py

[Install]
WantedBy=default.target
EOF
)
printf "systemd user service:\n####################\n\n"
printf "$SYSTEMD_SERVICE_CONTENT\n\n####################\n\n"


printf "Writing systemd user service: '\"$SYSTEMD_SERVICE_CONTENT\" > ~/.config/systemd/user/steam-showots.service'\n"
echo "$SYSTEMD_SERVICE_CONTENT" > ~/.config/systemd/user/steam-showots.service
printf "Systemd user service file written...\n\n"


printf "Activating user service immediately: 'systemctl enable --now --user steam-showots.service'\n"
systemctl enable --now --user steam-showots.service
printf "Systemd user service enabled...\n\n"

printf "Done... To disable run 'systemctl disablöe --now --user steam-showots.service'\n"
