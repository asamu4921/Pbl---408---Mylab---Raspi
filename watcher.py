import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
import os
import mysql.connector
import time
import face_recognition

# Tanggal & Jam
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

def load_font_safe(path, size):
    if not os.path.exists(path):
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

font_path_extralight = "C:/python/mylab/Poppins-ExtraLight.ttf"
font_path_regular = "C:/python/mylab/Poppins-Regular.ttf"
font_28 = load_font_safe(font_path_extralight, 28)
font_32 = load_font_safe(font_path_extralight, 32)
font_35 = load_font_safe(font_path_regular, 35)
font_54 = load_font_safe(font_path_extralight, 54)
font_popup = load_font_safe(font_path_regular, 40)

def get_data_dosen_terbaru():
    data = []
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab'
        )
        cursor = conn.cursor()
        dosen_terdaftar = ['​Banu Failasuf, S.Tr ', '​Agus Riady, A.Md.Kom ', 'Supardianto, S.ST.M.Eng.','Sartikha, S. ST., M.Eng']
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
            data.append({"no": idx, "nama": nama, "status": status.upper()})
        cursor.close()
        conn.close()
    except:
        data = [
            {"no": 1, "nama": "​Banu Failasuf, S.Tr ", "status": "Tidak Ada"},
            {"no": 2, "nama": "​Agus Riady, A.Md.Kom ", "status": "Tidak Ada"},
            {"no": 3, "nama": "Supardianto, S.ST.M.Eng.", "status": "Tidak Ada"},
            {"no": 4, "nama": "Sartikha, S. ST., M.Eng", "status": "Tidak Ada"},
        ]
    return data

def get_status_terakhir(nama_dosen):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab'
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status FROM aktivitas_ruang_dosen
            WHERE nama_dosen = %s
            ORDER BY datetime DESC LIMIT 1
        """, (nama_dosen,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return row[0] if row else "Tidak Ada"
    except:
        return "Tidak Ada"

def insert_status(nama_dosen, status_baru):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab'
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO aktivitas_ruang_dosen (nama_dosen, status, datetime)
            VALUES (%s, %s, NOW())
        """, (nama_dosen, status_baru))
        conn.commit()
        cursor.close()
        conn.close()
    except:
        pass

def draw_text(img, text, pos, font, color=(255, 255, 255)):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)

def tampilkan_panel_dosen():
    width, height = 1280, 720
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = (167, 101, 47)
    img = draw_text(img, get_tanggal(), (40, 30), font_28)
    img = draw_text(img, get_jam(), (40, 70), font_28)
    img = draw_text(img, "RUANG DOSEN 1", (40, 220), font_54)
    cv2.line(img, (40, 300), (1240, 300), (255, 255, 255), 2)
    y_header = 350
    img = draw_text(img, "NO", (80, y_header), font_35)
    img = draw_text(img, "NAMA DOSEN", (200, y_header), font_35)
    img = draw_text(img, "STATUS", (900, y_header), font_35)
    data_dosen = get_data_dosen_terbaru()
    y = y_header + 50
    for data in data_dosen:
        img = draw_text(img, str(data["no"]), (80, y), font_32)
        img = draw_text(img, data["nama"], (200, y), font_32)
        img = draw_text(img, data["status"], (900, y), font_32)
        y += 60
    return img

dataset_folder = "dataset"
known_encodings = []
known_names = []
for filename in os.listdir(dataset_folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join(dataset_folder, filename)
        img = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(filename)[0].upper())

cap = cv2.VideoCapture(0)
cv2.namedWindow("RUANG DOSEN 1", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("RUANG DOSEN 1", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

last_seen = {}
reset_delay = 3
popup_time = 2
popup_active = False
popup_start = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            panel = tampilkan_panel_dosen()
            cv2.imshow("RUANG DOSEN 1", panel)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        rgb_frame = frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        wajah_dikenali = []

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            name = "Wajah Tidak Dikenal"
            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
            wajah_dikenali.append((name, face_location))

        now = time.time()
        if wajah_dikenali:
            for name, (top, right, bottom, left) in wajah_dikenali:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
                if name in known_names:
                    seen = last_seen.get(name, {"seen": False, "last_time": 0})
                    if not seen["seen"]:
                        status_terakhir = get_status_terakhir(name)
                        status_baru = "Tidak Ada" if status_terakhir.upper() == "ADA" else "Ada"
                        insert_status(name, status_baru)
                        last_seen[name] = {"seen": True, "last_time": now}
                        popup_active = True
                        popup_start = now
                    else:
                        last_seen[name]["last_time"] = now

            # Tampilkan popup centang jika aktif
            if popup_active and time.time() - popup_start <= popup_time:
                popup = Image.fromarray(frame)
                draw = ImageDraw.Draw(popup)
                draw.ellipse((1000, 40, 1080, 120), fill=(0, 255, 0))
                draw.text((1090, 50), "✔", font=font_popup, fill=(0, 255, 0))
                draw.text((1000, 125), "Sukses", font=font_popup, fill=(0, 255, 0))
                frame = np.array(popup)
            elif popup_active:
                popup_active = False

            cv2.imshow("RUANG DOSEN 1", frame)
        else:
            panel = tampilkan_panel_dosen()
            cv2.imshow("RUANG DOSEN 1", panel)

        for name in list(last_seen.keys()):
            if now - last_seen[name]["last_time"] > reset_delay:
                last_seen[name]["seen"] = False

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    pass

cap.release()
cv2.destroyAllWindows()
