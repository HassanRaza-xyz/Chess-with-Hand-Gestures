import urllib.request
import os

with open("piece_urls.txt") as f:
    for line in f:
        name, url = line.strip().split()
        out_path = os.path.join(os.path.dirname(__file__), name)
        if not os.path.exists(out_path):
            print(f"Downloading {name} ...")
            urllib.request.urlretrieve(url, out_path)
print("All pieces downloaded.")
