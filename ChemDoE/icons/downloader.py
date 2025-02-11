import os
import shutil

import cairosvg
import requests
from bs4 import BeautifulSoup

# Bootstrap Icons URL
# FontAwesome metadata URL
FA_ICONS_URL = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/metadata/icons.json"
FA_BASE_URL = "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/svgs/solid/"


def run_download(output_folder: str = "fontawesome-icons"):
    # Folder to save icons
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.makedirs(output_folder, exist_ok=True)

    # Get the Bootstrap Icons page
    # Fetch icon metadata
    response = requests.get(FA_ICONS_URL)
    if response.status_code != 200:
        print("Failed to fetch FontAwesome icons metadata.")
        exit(1)

    icons = response.json()

    # Download each icon
    for icon_name in icons.keys():
        icon_url = f"{FA_BASE_URL}{icon_name}.svg"
        icon_path = os.path.join(output_folder, f"{icon_name}.svg.png")

        icon_response = requests.get(icon_url)
        if icon_response.status_code == 200:
            with open(icon_path, "wb") as file:
                png_data = cairosvg.svg2png(bytestring=icon_response.content, scale=2.0)
                file.write(png_data)
            print(f"Downloaded: {icon_name}.svg")
        else:
            print(f"Failed to download: {icon_name}.svg")

    print("Download complete.")


if __name__ == "__main__":
    run_download()