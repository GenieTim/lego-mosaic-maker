#!/usr/bin/env python

"""
This script updates the LEGO parts data by fetching the latest information from the Rebrickable website.

This is done in the following steps:
1. Open https://rebrickable.com/downloads/
2. Find all links with text "gzip", take the URLs,
3. Download the gzipped files,
4. Unzip the files,
5. Store the resulting CSV files in the `data` directory.
"""

import gzip
import os
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def get_gzip_download_links():
    """Scrape the Rebrickable downloads page for gzip file links."""
    url = "https://rebrickable.com/downloads/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Find all links containing "gzip" in their text
        gzip_links = []
        for link in soup.find_all("a", href=True):
            if link.text and "gzip" in link.text.lower():
                full_url = urljoin(url, link["href"])
                gzip_links.append(full_url)

        return gzip_links

    except requests.RequestException as e:
        print(f"Error fetching download page: {e}")
        return []


def download_and_extract_file(url, data_dir):
    """Download a gzipped file and extract it to the data directory."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"Downloading {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Get filename from URL, removing query parameters
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        # Extract CSV filename (remove .gz extension)
        if filename.endswith(".gz"):
            csv_filename = filename[:-3]
        else:
            csv_filename = filename + ".csv"

        # Decompress and save
        decompressed_data = gzip.decompress(response.content)
        csv_path = os.path.join(data_dir, csv_filename)

        with open(csv_path, "wb") as f:
            f.write(decompressed_data)

        print(f"Extracted to {csv_path}")
        return True

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return False


def update_lego_parts_data():
    """Main function to update LEGO parts data."""
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Fetching gzip download links...")
    gzip_links = get_gzip_download_links()

    if not gzip_links:
        print("No gzip links found on the downloads page.")
        return

    print(f"Found {len(gzip_links)} gzip files to download.")

    successful_downloads = 0
    for link in gzip_links:
        if download_and_extract_file(link, data_dir):
            successful_downloads += 1

    print(
        f"\nCompleted: {successful_downloads}/{len(gzip_links)} files downloaded and extracted."
    )


if __name__ == "__main__":
    update_lego_parts_data()
