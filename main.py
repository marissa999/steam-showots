#!/usr/bin/env python3

import os
import time
import websockets
import io
import asyncio
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



STEAM_PATH_LINUX = "~/.local/share/Steam"
STEAM_PATH_MAC = "~/Library/Application Support/Steam/userdata"
STEAM_PATH_WINDOWS = "C:\\Program Files (x86)\\Steam\\userdata"



def main():
	
	# Obtain a list of all user accounts
	user_accounts: [str] = list_user_accounts()

	# Obtain a list of all remote folders
	remote_folders: [str] = list_remote_folders(user_accounts)

	# Obtain a list of all screenshot folders
	screenshot_folders: [str] = list_screenshot_folders(remote_folders)

	event_handler = NewFileHandler(new_screenshot_found)
	observer = Observer()

	for folder in screenshot_folders:
		observer.schedule(event_handler, folder, recursive=False)

	observer.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()

	observer.join()


def get_steam_path() -> str:
	from sys import platform
	if platform == "linux" or platform == "linux2":
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



def list_screenshot_folders(steam_remote_folders: [str]) -> [str]:
	screenshot_folders: [str] = []

	for remote_folder in steam_remote_folders:

		if not os.path.exists(remote_folder):
			raise RuntimeError(f"Specified path does not exist: {remote_folder}")

		for folder in os.listdir(remote_folder):
			screenshot_folder_path = os.path.join(remote_folder, folder, 'screenshots')
			if os.path.exists(screenshot_folder_path):
				screenshot_folders.append(screenshot_folder_path)

	return screenshot_folders



class NewFileHandler(FileSystemEventHandler):
	def __init__(self, callback):
		super().__init__()
		self.callback = callback

	def on_created(self, event):
		self.callback(event.src_path)



def new_screenshot_found(screenshot_path: str):
	print(screenshot_path)
	image = Image.open(screenshot_path)
	async def asyncfunc():
		url = "ws://127.0.0.1:7331"
		async with websockets.connect(url) as ws:
			imgByteArr = io.BytesIO()
			image.save(imgByteArr, format=image.format)
			imgByteArr = imgByteArr.getvalue()
			await ws.send(imgByteArr)
	asyncio.run(asyncfunc())



if __name__ == "__main__":
	main()