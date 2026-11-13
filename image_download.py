# download one image per file

"""Download one image per item listed in collection_items_data.csv."""
import csv
import time
from pathlib import Path

import requests

# --- settings: change these paths if your folders move ---
OUT = Path(r'C:\Users\macke\OneDrive\Documents\Fall 2027 UMSI\SI_676\API_data\output')
SRC = OUT / 'collection_items_data.csv'   # input: the CSV from the transform step
IMG_DIR = OUT / 'item-files'              # output: where images are saved
HEADERS = {'User-Agent': 'Mozilla/5.0 (SI676 class project)'}


def download_image(url, out_file, tries=3):
    """Download one image with retries. Returns True on success."""
    for attempt in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
        except requests.exceptions.RequestException as e:
            print('request error:', e)
            time.sleep(5 * (attempt + 1))
            continue
        if r.status_code == 200:
            out_file.write_bytes(r.content)
            return True
        print(r.status_code, url)
        time.sleep(5 * (attempt + 1))
    return False


def main():
    if not SRC.exists():
        raise FileNotFoundError(f'CSV not found: {SRC}')

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    saved, failed = 0, []

    with open(SRC, 'r', encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            item_id = row['item_id']
            url = row['image_url'].split('#')[0]   # drop the #h=..&w=.. part

            if not url:
                failed.append((item_id, 'no image url'))
                continue

            out_file = IMG_DIR / f'{item_id}{Path(url).suffix or ".jpg"}'

            if out_file.exists():                  # skip ones already downloaded
                saved += 1
                continue

            if download_image(url, out_file):
                saved += 1
                print('saved', out_file.name)
            else:
                failed.append((item_id, url))

            time.sleep(1)                          # be polite to the server

    print('\nsaved', saved, 'images')
    print('failed:', len(failed))