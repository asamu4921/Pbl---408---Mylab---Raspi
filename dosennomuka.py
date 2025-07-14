import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
import os
import mysql.connector
import face_recognition
import pickle

# ---------------------------
# MAPPING TANGGAL & JAM
# ---------------------------
hari_mapping = {
    "Monday": "Senin", "Tuesday": "Selasa", "Wednesday": "Rabu",
    "Thursday": "Kamis", "Friday": "Jumat", "Saturday": "Sabtu", "Sunday": "Minggu"
}
bulan_mapping = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni", "July": "Juli",
    "August": "Agustus", "September": "September", "October": "Oktober",
    "November": "November", "December": "Desember"
}
def get_tanggal():
    now = datetime.now()
    hari = hari_mapping[now.strftime("%A")]
    tanggal = now.strftime("%d")
    bulan = bulan_mapping[now.strftime("%B")]
    tahun = now.strftime("%Y")
    return f"{hari}, {tanggal} {bulan} {tahun}"

def get_jam():
    return datetime.now().strftime("%H:%M:%S")

# ---------------------------
# FONT SAFE
# ---------------------------
def load_font_safe(path, size):
    if not os.path.exists(path):
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

font_path = "C:/python/mylab/Poppins-ExtraLight.ttf"
font_28 = load_font_safe(font_path, 28)
font_32 = load_font_safe(font_path, 32)
font_54 = load_font_safe(font_path, 54)

# ---------------------------
# MYSQL
# ---------------------------
dosen_terdaftar = [
    'Banu Failasuf, S.Tr',
    'Ahmad Saif Almuflihin',
    'ridho',
    'wali'
]

def get_data_dosen():
    data = []
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab'
        )
        cursor = conn.cursor()
        for idx, nama in enumerate(dosen_terdaftar, start=1):
            query = """
                SELECT status FROM aktivitas_ruang_dosen
                WHERE nama_dosen = %s
                ORDER BY datetime DESC
                LIMIT 1
            """
            cursor.execute(query, (nama,))
            row = cursor.fetchone()
            status = row[0] if row else "Tidak Ada"
            data.append({"no": idx, "nama": nama, "status": status})
        cursor.close()
        conn.close()
    except:
        for idx, nama in enumerate(dosen_terdaftar, start=1):
            data.append({"no": idx, "nama": nama, "status": "Tidak Ada"})
    return data

def ubah_status(nama_dosen, status_baru):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab'
        )
        cursor = conn.cursor()
        query = """
            INSERT INTO aktivitas_ruang_dosen (nama_dosen, status, datetime)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (nama_dosen, status_baru))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"[INFO] Status {nama_dosen} diubah jadi {status_baru}")
    except Exception as e:
        print("[MYSQL ERROR]", e)

# ---------------------------
# DRAW TEXT
# ---------------------------
def draw_text(img, text, pos, font, color=(255,255,255)):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)

# ---------------------------
# PANEL DOSEN
# ---------------------------
def tampilkan_panel():
    width, height = 1280, 720
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = (167, 101, 47)

    img = draw_text(img, get_tanggal(), (40, 30), font_28)
    img = draw_text(img, get_jam(), (40, 70), font_28)
    img = draw_text(img, "RUANG DOSEN 1", (40, 220), font_54)
    cv2.line(img, (40, 300), (1240, 300), (255,255,255), 2)

    y_header = 350
    img = draw_text(img, "NO", (80, y_header), font_32)
    img = draw_text(img, "NAMA DOSEN", (200, y_header), font_32)
    img = draw_text(img, "STATUS", (900, y_header), font_32)

    data_dosen = get_data_dosen()
    y = y_header + 50
    for data in data_dosen:
        img = draw_text(img, str(data["no"]), (80, y), font_32)
        img = draw_text(img, data["nama"], (200, y), font_32)
        img = draw_text(img, data["status"].upper(), (900, y), font_32)
        y += 60

    return img

# ---------------------------
# LOAD FACE ENCODING
# ---------------------------
with open("encodings.pkl", "rb") as f:
    encodings_data = pickle.load(f)

# ---------------------------
# STATE MACHINE
# ---------------------------
cv2.namedWindow("RUANG DOSEN 1", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("RUANG DOSEN 1", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

mode = "panel"
detected_name = None
cap = None

try:
    while True:
        if mode == "panel":
            panel = tampilkan_panel()
            cv2.imshow("RUANG DOSEN 1", panel)
            key = cv2.waitKey(500) & 0xFF

            if key == ord('k'):
                mode = "kamera"
            elif key == ord('q'):
                break

        elif mode == "kamera":
            if cap is None:
                cap = cv2.VideoCapture(0)

            ret, frame = cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                matches = face_recognition.compare_faces(encodings_data["encodings"], encoding, tolerance=0.5)
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = encodings_data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
                    if name in dosen_terdaftar:
                        detected_name = name
                        mode = "konfirmasi"
                        cap.release()
                        cap = None
                        break

            cv2.imshow("RUANG DOSEN 1", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break

        elif mode == "konfirmasi":
            width, height = 1280, 720
            img = np.zeros((height, width, 3), dtype=np.uint8)
            img[:, :] = (0, 0, 0)
            teks = f"Wajah: {detected_name}\nApakah mau ubah status?\nY = Ya | N = Tidak"
            y = 200
            for line in teks.split("\n"):
                img = draw_text(img, line, (100, y), font_54)
                y += 80

            cv2.imshow("RUANG DOSEN 1", img)
            key = cv2.waitKey(200) & 0xFF

            if key == ord('y'):
                # Cari status sekarang
                data = get_data_dosen()
                status_now = "Tidak Ada"
                for d in data:
                    if d["nama"] == detected_name:
                        status_now = d["status"]
                        break
                status_next = "Tidak Ada" if status_now == "Ada" else "Ada"
                ubah_status(detected_name, status_next)
                mode = "panel"
                detected_name = None

            elif key == ord('n'):
                mode = "panel"
                detected_name = None

            elif key == ord('q'):
                break

except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
