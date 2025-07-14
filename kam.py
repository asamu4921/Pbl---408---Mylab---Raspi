import face_recognition
import cv2
import os
import pickle

# Path dataset
DATASET_DIR = 'dataset'

known_encodings = []
known_names = []

for person_name in os.listdir(DATASET_DIR):
    person_folder = os.path.join(DATASET_DIR, person_name)
    if not os.path.isdir(person_folder):
        continue

    for filename in os.listdir(person_folder):
        filepath = os.path.join(person_folder, filename)
        print(f"[INFO] Processing {filepath}")

        # Load + resize gambar
        image = cv2.imread(filepath)
        if image is None:
            print(f"[WARN] Failed to load {filepath}")
            continue

        # Resize ke max lebar 500px biar ringan
        h, w = image.shape[:2]
        if w > 500:
            scale = 500 / w
            image = cv2.resize(image, (0,0), fx=scale, fy=scale)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect & encode
        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(person_name)

# Simpan ke pickle
data = {"encodings": known_encodings, "names": known_names}
with open("encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print("[INFO] Encoding selesai & disimpan ke encodings.pkl")
