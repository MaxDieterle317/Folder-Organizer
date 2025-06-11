# Import necessary Python modules (tools that help us perform tasks)
import os                      # For interacting with the operating system (not used directly here, but common for file tasks)
import shutil                  # For moving files around
import argparse                # For reading input from the command line
import json                    # For reading configuration files in JSON format
from pathlib import Path       # For working with file and folder paths
import logging                 # For keeping a log (record) of actions

# Set up a log file to keep track of what happens when the script runs
logging.basicConfig(
    filename="organizer.log",                     # Log messages will be saved in this file
    level=logging.INFO,                           # Log only informational messages and above (not debug messages)
    format="%(asctime)s - %(levelname)s - %(message)s"  # How each log entry will be formatted
)

# A dictionary (lookup table) that maps file types (like 'images') to a list of file extensions
# These are the file types the script will recognize and organize
FOLDER_MAP = {
    "images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff"],
    "documents": ["pdf", "docx", "doc", "txt", "xls", "xlsx", "ppt", "pptx"],
    "videos": ["mp4", "avi", "mkv", "mov"],
    "music": ["mp3", "wav", "flac", "aac"],
    "archives": ["zip", "rar", "tar", "gz", "7z"],
    "executables": ["exe", "msi", "dmg", "deb", "rpm"],
}

# Define the default folder locations (change these as needed)
DOWNLOADS = Path("Put your download folder directory here")         # Folder where files are downloaded
HOME = Path("Put where you want the folders here")  # Base location where organized folders will be created
HOME.mkdir(parents=True, exist_ok=True)              # Create the HOME folder if it doesn't already exist

# Mapping of file categories to their destination folders
DEST_FOLDERS = {
    "images": HOME / "Pictures",
    "documents": HOME / "Documents",
    "videos": HOME / "Videos",
    "music": HOME / "Music",
    "archives": HOME / "Archives",
    "executables": HOME / "Executables",
}

# This function handles input options from the command line
def parse_args():
    parser = argparse.ArgumentParser(description="Organize Downloads Folder by File Type")
    parser.add_argument("--config", type=str, default="config.json", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without moving files")
    return parser.parse_args()

# This function loads a config file if one exists, and updates folder locations and file types accordingly
def load_config(config_path="config.json"):
    global DOWNLOADS, DEST_FOLDERS, FOLDER_MAP  # Let Python know we are modifying the global variables

    config_file = Path(config_path)
    if config_file.exists():  # Check if config file is present
        with open(config_file, "r") as f:
            config = json.load(f)  # Read the file and load it into a dictionary

        # Update the download folder if specified
        if "downloads_folder" in config:
            DOWNLOADS = Path(config["downloads_folder"]).expanduser()

        # Update the destination folders if specified
        if "folders" in config:
            for key in config["folders"]:
                DEST_FOLDERS[key] = Path(config["folders"][key]).expanduser()

        # Update the folder map (extensions) if specified
        if "extensions" in config:
            FOLDER_MAP = config["extensions"]

# This function extracts the file extension from a file path
def get_extension(file_path):
    return file_path.suffix.lower().strip(".")  # ".jpg" → "jpg"

# If a file already exists in the destination, this adds a number to the file name to avoid overwriting
def resolve_duplicate(dest_folder, filename):
    base = filename.stem  # The name without extension
    ext = filename.suffix # The file extension
    counter = 1
    new_name = filename
    while (dest_folder / new_name).exists():  # Keep looping until a unique name is found
        new_name = Path(f"{base}({counter}){ext}")
        counter += 1
    return new_name

# This is the main function that organizes files in the Downloads folder
def organize_downloads(dry_run=False):
    if not DOWNLOADS.exists():  # If the downloads folder doesn’t exist, show an error
        print(f"[ERROR] Downloads folder not found: {DOWNLOADS}")
        return

    # Go through each file in the Downloads folder
    for item in DOWNLOADS.iterdir():
        if item.is_file():  # Skip folders, only process files
            ext = get_extension(item)
            for category, extensions in FOLDER_MAP.items():
                if ext in extensions:
                    dest_folder = DEST_FOLDERS.get(category)
                    if not dest_folder:
                        continue

                    dest_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn’t exist

                    # Create a safe name in case file already exists
                    new_name = resolve_duplicate(dest_folder, item.name if isinstance(item.name, Path) else Path(item.name))
                    dest_path = dest_folder / new_name

                    if dry_run:
                        # In dry-run mode, just print what would happen
                        print(f"[Dry-Run] Would move: {item.name} → {dest_path}")
                    else:
                        # Actually move the file and log the action
                        shutil.move(str(item), str(dest_path))
                        print(f"Moved: {item.name} → {dest_path}")
                        logging.info(f"Moved {item} to {dest_path}")
                    break  # Once moved, no need to check other categories

# This part runs only when the script is run directly from the command line
if __name__ == "__main__":
    args = parse_args()            # Read the input arguments
    load_config(args.config)       # Load settings from config file (if available)
    organize_downloads(dry_run=args.dry_run)  # Start organizing files!

# ---------------------------------------
# How to run this script:
#
# Open Command Prompt (Terminal), then type:
#
# 1. Regular Mode (will move files):
#    python "Directory where script is located" --config config.json
#
# 2. Dry Run Mode (just shows what would happen without moving files):
#    python "Directory where script is located" --config config.json --dry-run
#
# Make sure Python is installed and added to your PATH.
# ---------------------------------------
