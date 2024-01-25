# steam-showots

Python script that sends a Steam screenshot after it was taken to a websocket from owocr for text recognition.
Python script can run in the background as a service.

Relies on https://github.com/AuroraWright/owocr

### Installation

```
git clone https://github.com/marissa999/steam-showots.git
cd steam-showots
./linux_install.sh
```

### Configuration

Location for config file is `~/.config/showots.ini`

Example:
```
[general]
host=192.168.178.90
port=7331
```
