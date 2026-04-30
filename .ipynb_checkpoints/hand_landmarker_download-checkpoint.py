import urllib.request
url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
print("Downloading hand_landmarker.task ...")
urllib.request.urlretrieve(url, "hand_landmarker.task")
print("Download complete.")
