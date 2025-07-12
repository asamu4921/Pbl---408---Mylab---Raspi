import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
import os
import mysql.connector
import time as time_module

# ---------------------------
# FUNGSI UNTUK TANGGAL & JAM
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
# FUNGSI LOAD FONT AMAN
# ---------------------------
def load_font_safe(path, size):
    if not os.path.exists(path):
        print(f"[ERROR] Font tidak ditemukan: {path}")
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"[ERROR] Gagal load font '{path}': {e}")
        return ImageFont.load_default()

# ---------------------------
# LOAD FONT
# ---------------------------
font_path_extralight = "C:/python/mylab/Poppins-ExtraLight.ttf"
font_28 = load_font_safe(font_path_extralight, 28)
font_32 = load_font_safe(font_path_extralight, 32)
font_54 = load_font_safe(font_path_extralight, 54)

# ---------------------------
# AMBIL DATA DOSEN DARI MYSQL
# ---------------------------
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

        dosen_terdaftar = ['Banu Failasuf, S.Tr', 'Agus Riady, A.Md.Kom', 'Supardianto, S.ST.M.Eng.','Sartikha, S. ST., M.Eng']
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
    except mysql.connector.Error as err:
        print(f"[MYSQL ERROR] {err}")
        # Jika error, fallback data dummy
        data = [
            {"no": 1, "nama": "Banu Failasuf, S.Tr", "status": "Tidak Ada"},
            {"no": 2, "nama": "Agus Riady, A.Md.Kom", "status": "Tidak Ada"},
            {"no": 3, "nama": "Supardianto, S.ST.M.Eng.", "status": "Tidak Ada"},
            {"no": 4, "nama": "Sartikha, S. ST., M.Eng", "status": "Tidak Ada"},
        ]
    return data

# ---------------------------
# DRAW TEXT KE LAYAR
# ---------------------------
def draw_text(img, text, pos, font, color=(255, 255, 255)):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)

# ---------------------------
# RENDER PANEL DOSEN
# ---------------------------
def tampilkan_panel_dosen():
    width, height = 1280, 720
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = (167, 101, 47)  # background

    # Header: Tanggal & Jam
    img = draw_text(img, get_tanggal(), (40, 30), font_28)
    img = draw_text(img, get_jam(), (40, 70), font_28)

    # Judul Panel
    img = draw_text(img, "RUANG DOSEN 1", (40, 220), font_54)

    # Garis pemisah
    cv2.line(img, (40, 300), (1240, 300), (255, 255, 255), 2)

    # Header Tabel
    y_header = 350
    img = draw_text(img, "NO", (80, y_header), font_32)
    img = draw_text(img, "NAMA DOSEN", (200, y_header), font_32)
    img = draw_text(img, "STATUS", (900, y_header), font_32)

    # Isi data dari MySQL
    data_dosen = get_data_dosen_terbaru()

    y = y_header + 50
    for data in data_dosen:
        img = draw_text(img, str(data["no"]), (80, y), font_32)
        img = draw_text(img, data["nama"], (200, y), font_32)
        img = draw_text(img, data["status"], (900, y), font_32)
        y += 60

    return img

# ---------------------------
# MAIN LOOP
# ---------------------------
cv2.namedWindow("RUANG DOSEN 1", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("RUANG DOSEN 1", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

try:
    while True:
        panel = tampilkan_panel_dosen()
        cv2.imshow("RUANG DOSEN 1", panel)
        key = cv2.waitKey(1000)
        if key == 27:  # tekan ESC
            break
except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
