#!/usr/bin/env python3

import os
import sys
import time
import websockets
import io
import asyncio
import configparser
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



# CONSTANTS
STEAM_PATH_LINUX: str = "~/.local/share/Steam"
STEAM_PATH_MAC: str = "~/Library/Application Support/Steam"
STEAM_PATH_WINDOWS: str = "C:\\Program Files (x86)\\Steam"

# CONFIG VARIABLES
websocket_host: str = '127.0.0.1'
websocket_port: str = '7331'



def main():

	# Read config
	config_file = os.path.join(os.path.expanduser('~'),'.config','showots.ini')
	config = configparser.ConfigParser()
	res = config.read(config_file)

	if len(res) != 0:
		try:
			global websocket_host
			websocket_host = config['general']['host'].strip()
		except KeyError:
			pass

		try:
			global websocket_port
			websocket_port = config['general']['port'].strip()
		except KeyError:
			pass

	# Obtain a list of all user accounts
	user_accounts: [str] = list_user_accounts()

	# Obtain a list of all remote folders
	remote_folders: [str] = list_remote_folders(user_accounts)

	# Setup observers
	event_handler = NewFileHandler(new_screenshot_found)
	observer = Observer()

	for folder in remote_folders:
		observer.schedule(event_handler, folder, recursive=True)

	observer.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()

	observer.join()


def get_steam_path() -> str:
	from sys import platform
	if platform == "linux":
		return os.path.expanduser(STEAM_PATH_LINUX)
	elif platform == "darwin":
		return os.path.expanduser(STEAM_PATH_MAC)
	elif platform == "win32":
		return os.path.expanduser(STEAM_PATH_WINDOWS)
	else:
		print("Unsupported operating system")
		raise RuntimeError("Unsupported operating system")



def list_user_accounts() -> [str]:
	# Path to the Steam userdata folder
	steam_path: str = get_steam_path()
	steam_accounts_path: str = os.path.join(steam_path, "userdata")

	# Check if the specified path exists
	if os.path.exists(steam_accounts_path):
		return [folder for folder in os.listdir(steam_accounts_path) if os.path.isdir(os.path.join(steam_accounts_path, folder))]
	else:
		print(f"Specified path does not exist: {steam_accounts_path}")
		raise RuntimeError(f"Specified path does not exist: {steam_accounts_path}")



def list_remote_folders(steam_userdata_accounts: [str]) -> [str]:
	remote_folders: [str] = []

	for account in steam_userdata_accounts:

		# If folder 760 (screenshots) does not already exist, create it
		path_folder_760: str = os.path.join(get_steam_path(), 'userdata', account, '760')
		if not os.path.exists(path_folder_760):
			os.mkdir(path_folder_760)

		# If folder remote (screenshots) does not already exist, create it
		path_folder_remote: str = os.path.join(path_folder_760, 'remote')
		if not os.path.exists(path_folder_remote):
			os.mkdir(path_folder_remote)

		remote_folders.append(path_folder_remote)

	return remote_folders



class NewFileHandler(FileSystemEventHandler):
	def __init__(self, callback):
		super().__init__()
		self.callback = callback

	def on_created(self, event):
		# Ignore folders
		if not event.is_directory:
			# Skip thumbmails 
			if os.path.basename(os.path.dirname(event.src_path)) != "thumbnails":
				self.callback(event.src_path)



def new_screenshot_found(screenshot_path: str):
	print(f"Screenshot found at {screenshot_path}")
	image: Image = None
	try:
		image = Image.open(screenshot_path)
	except Exception:
		print(f"Unable to open {screenshot_path}")
		return
	async def asyncfunc():
		url = "ws://{}:{}".format(websocket_host, websocket_port)
		try:
			async with websockets.connect(url) as ws:
				imgByteArr = io.BytesIO()
				image.save(imgByteArr, format=image.format)
				imgByteArr = imgByteArr.getvalue()
				await ws.send(imgByteArr)
		except ConnectionRefusedError:
			print(f"Unable to connect to {url}")
		sys.stdout.flush()
	asyncio.run(asyncfunc())



if __name__ == "__main__":
	main()
