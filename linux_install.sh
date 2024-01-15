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
