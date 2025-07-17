import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime, time as dt_time
import time as time_module
import os
import pymysql
import face_recognition
import pickle
# -------------------------------
# FUNGSI TERJEMAH HARI & BULAN
# -------------------------------
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

# -------------------------------
# LOAD FONT AMAN
# -------------------------------
def load_font_safe(path, size):
    if not os.path.exists(path):
        print(f"[ERROR] Font tidak ditemukan: {path}")
        return ImageFont.load_default()
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"[ERROR] Gagal load font '{path}': {e}")
        return ImageFont.load_default()

# Font Paths
font_path_black = "C:/python/mylab/Poppins-Black.ttf"
font_path_extralight = "C:/python/mylab/Poppins-ExtraLight.ttf"
font_path_regular = "C:/python/mylab/Poppins-Regular.ttf"
font_path_bold = "C:/python/mylab/Poppins-Bold.ttf"

# Load fonts
font_poppins_20 = load_font_safe(font_path_black, 20)
font_poppins_24 = load_font_safe(font_path_extralight, 25)
font_poppins_28 = load_font_safe(font_path_extralight, 28)
font_poppins_32 = load_font_safe(font_path_regular, 32)
font_poppins_40 = load_font_safe(font_path_extralight, 54)
font_poppins_48 = load_font_safe(font_path_black, 48)
font_poppins_64 = load_font_safe(font_path_bold, 68)
font_poppins_84 = load_font_safe(font_path_black, 84)
font_extralight_28 = load_font_safe(font_path_extralight, 28)

# fungsi load encodings()
def load_encodings(path="encodings.pkl"):
    with open(path, "rb") as f:
        return pickle.load(f)
# fungsi run camera 
def run_camera(encodings_data):
    cap = cv2.VideoCapture(0)
    detected_name = None

    while True:
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
                detected_name = max(counts, key=counts.get)
                break

        cv2.imshow("Kamera", frame)
        key = cv2.waitKey(1) & 0xFF

        if detected_name:
            break

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return detected_name
# fungsi konfirmasi dan insert
def konfirmasi_dan_insert(nama):
    print(f"Terdeteksi: {nama}")
    jawab = input("Yakin insert data? (y/n): ")
    if jawab.lower() == 'y':
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='gpuasamu',
                database='mylab'
            )
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO aktivitas_ruang_lab (nama_laboran, status, datetime)
                VALUES (%s, %s, NOW())
                """
                cursor.execute(sql, (nama, 'Normal'))
                conn.commit()
                print(f"[INFO] Insert OK: {nama} - Normal")
            conn.close()
        except Exception as e:
            print(f"[ERROR] {e}")
    else:
        print("Dibatalkan.")

# -------------------------------
# AMBIL DATA REAL DARI DATABASE
# -------------------------------
def ambil_jadwal_matkul():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT matkul, start_time, end_time, kelas, dosen, hari 
                FROM jadwal_matkul 
                WHERE kode_ruangan = 'RTF.IV.4' AND hari = %s 
                ORDER BY start_time
            """, (hari_mapping[datetime.now().strftime("%A")],))
            results = cursor.fetchall()
        conn.close()

        jadwal = []
        for row in results:
            start = datetime.strptime(str(row["start_time"]), "%H:%M:%S").time()
            end = datetime.strptime(str(row["end_time"]), "%H:%M:%S").time()
            jadwal.append((
                row["matkul"],     # nama
                "Mata Kuliah",     # kegiatan fix
                start,
                end,
                f"{row['dosen']} ({row['kelas']})"  # penanggung
            ))
        return jadwal
    except Exception as e:
        print(f"[DB ERROR MATKUL] {e}")
        return []

def ambil_jadwal_rtf():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    nama_mahasiswa,
                    jenis_kegiatan,
                    nama_kegiatan_other,
                    start_time,
                    end_time,
                    nama_penanggungjawab
                FROM api
                WHERE kode_ruangan = 'rtf.iv.4' AND tanggal_pinjam = CURDATE()
                ORDER BY start_time
            """)
            results = cursor.fetchall()
        conn.close()

        jadwal = []
        for row in results:
            kegiatan = (
                row["nama_kegiatan_other"] if row["jenis_kegiatan"].lower() != "pbl"
                else "PBL"
            )
            start = datetime.strptime(str(row["start_time"]), "%H:%M:%S").time()
            end = datetime.strptime(str(row["end_time"]), "%H:%M:%S").time()
            jadwal.append((
                row["nama_mahasiswa"],
                kegiatan,
                start,
                end,
                row["nama_penanggungjawab"]
            ))

        return jadwal

    except Exception as e:
        print(f"[DB ERROR] {e}")
        return []

# -------------------------------
# FUNGSI DRAW TEXT
# -------------------------------
def draw_text(img, text, pos, font, color=(255, 255, 255), return_size=False):
    if return_size:
        dummy_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        return draw.textsize(text, font=font)
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)

# -------------------------------
# FUNGSI: Ambil status laboran terbaru
# -------------------------------
def get_status_laboran(nama):
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='gpuasamu',
            database='mylab',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT status 
                FROM aktivitas_ruang_lab 
                WHERE nama_laboran = %s 
                ORDER BY datetime DESC 
                LIMIT 1
            """, (nama,))
            result = cursor.fetchone()
        conn.close()
        if result:
            return result['status']
        else:
            return "Normal"
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return "Normal"

# -------------------------------
# FUNGSI PANEL
# -------------------------------
def tampilkan_panel(slide_index_selesai, slide_index_berikutnya):
    jadwal_api = ambil_jadwal_rtf()
    jadwal_matkul = ambil_jadwal_matkul()

    # Filter bentrok
    def is_bentrok(start1, end1, start2, end2):
        return start1 < end2 and start2 < end1

    jadwal_api_bersih = []
    for api in jadwal_api:
        api_start, api_end = api[2], api[3]
        bentrok = False
        for mk in jadwal_matkul:
            mk_start, mk_end = mk[2], mk[3]
            if is_bentrok(api_start, api_end, mk_start, mk_end):
                bentrok = True
                break
        if not bentrok:
            jadwal_api_bersih.append(api)

    jadwal = jadwal_api_bersih + jadwal_matkul

    # Buat panel dasar
    width, height = 1280, 720
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :850] = (167, 101, 47)
    img[:, 850:] = (64, 35, 12)

    now = datetime.now().time()
    img = draw_text(img, get_tanggal(), (40, 30), font_extralight_28)
    img = draw_text(img, get_jam(), (40, 70), font_extralight_28)
    img = draw_text(img, "RTF.IV.4", (40, 220), font_poppins_40)
    cv2.line(img, (40, 300), (830, 300), (255, 255, 255), 2)

    sedang_berlangsung = None
    selesai = []
    berikutnya = []

    for row in jadwal:
        nama, kegiatan, start, end, penanggung = row
        if start <= now <= end:
            sedang_berlangsung = row
        elif end < now:
            selesai.append(row)
        elif start > now:
            berikutnya.append(row)

    # -------------------------------
    # Cek status laboran
    # -------------------------------
    status_terbaru = get_status_laboran("Ahmad Saif Almuflihin")
    if status_terbaru.lower() != "normal":
        override_status = f"MOHON MAAF RUANGAN INI SEDANG {status_terbaru.upper()}!"
        sedang_berlangsung = None  # Matikan jadwal real
    else:
        override_status = None

    # DEBUG
    print(f"[DEBUG] Sekarang: {datetime.now().strftime('%H:%M:%S')}")
    print(f"[SEDANG BERLANGSUNG]: {sedang_berlangsung}")
    print(f"[SELESAI]: {selesai}")
    print(f"[BERIKUTNYA]: {berikutnya}")

    img = draw_text(img, "Tidak Tersedia" if not sedang_berlangsung and not override_status else "Tersedia", (40, 295), font_poppins_64)

    # -------------------------------
    # Panel Sedang Berlangsung
    # -------------------------------
    y_sb = 400
    img = draw_text(img, "Sedang Berlangsung :", (40, y_sb), font_poppins_24)

    if override_status:
        img = draw_text(img, override_status, (40, y_sb + 70), font_poppins_28)
    else:
        if sedang_berlangsung:
            nama, kegiatan, start, end, penanggung = sedang_berlangsung
            waktu_str = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        else:
            nama, kegiatan, waktu_str, penanggung = "-", "-", "-", "-"

        labels = ["Peminjam", "Kegiatan", "Waktu", "Penanggung Jawab"]
        values = [nama, kegiatan, waktu_str, penanggung]

        font = font_poppins_28
        line_spacing = int(font.size * 0.9)
        y_offset = y_sb + 70
        max_label_width = max([draw_text(None, l, (0, 0), font, return_size=True)[0] for l in labels])

        for label, value in zip(labels, values):
            x_label, x_colon, x_value = 40, 40 + max_label_width + 5, 40 + max_label_width + 15
            if label == "Penanggung Jawab":
                img = draw_text(img, "Penanggung", (x_label, y_offset), font)
                img = draw_text(img, ":", (x_colon, y_offset), font)
                img = draw_text(img, value, (x_value, y_offset), font)
                y_offset += int(line_spacing * 0.9)
                img = draw_text(img, "Jawab", (x_label, y_offset), font)
                y_offset += int(line_spacing * 1.2)
            else:
                img = draw_text(img, label, (x_label, y_offset), font)
                img = draw_text(img, ":", (x_colon, y_offset), font)
                img = draw_text(img, value, (x_value, y_offset), font)
                y_offset += line_spacing + 20
    # Panel kanan - Jadwal Selesai & Berikutnya
    cv2.line(img, (860, 300), (1270, 300), (180, 180, 180), 1)
    x_right = 870

    # Jadwal Selesai
    y_start = 50
    img = draw_text(img, "Jadwal Selesai :", (x_right, y_start), font_poppins_32)
    if selesai:
        row = selesai[slide_index_selesai % len(selesai)]
        nama, kegiatan, start, end, penanggung = row
        waktu_str = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        if kegiatan == "Mata Kuliah":
            labels = ["Mata Kuliah", "Waktu", "Dosen", "Kelas"]
            penanggung_split = penanggung.split("(")
            dosen = penanggung_split[0].strip()
            kelas = penanggung_split[1].replace(")", "").strip() if len(penanggung_split) > 1 else "-"
            values = [nama, waktu_str, dosen, kelas]
        else:
            labels = ["Peminjam", "Kegiatan", "Waktu", "Penanggung Jawab"]
            values = [nama, kegiatan, waktu_str, penanggung]

        y_offset = y_start + 50
        for label, value in zip(labels, values):
            x_label, x_colon, x_value = x_right, x_right + 170, x_right + 185
            if label == "Penanggung Jawab":
                img = draw_text(img, "Penanggung", (x_label, y_offset), font_poppins_24)
                img = draw_text(img, ":", (x_colon, y_offset), font_poppins_24)
                img = draw_text(img, value, (x_value, y_offset), font_poppins_24)
                y_offset += int(font_poppins_24.size * 0.9)
                img = draw_text(img, "Jawab", (x_label, y_offset), font_poppins_24)
                y_offset += int(font_poppins_24.size * 1.2)
            else:
                img = draw_text(img, label, (x_label, y_offset), font_poppins_24)
                img = draw_text(img, ":", (x_colon, y_offset), font_poppins_24)
                img = draw_text(img, value, (x_value, y_offset), font_poppins_24)
                y_offset += int(font_poppins_24.size * 0.9) + 10

    # Jadwal Berikutnya
    y2 = 430
    img = draw_text(img, "Jadwal Berikutnya :", (x_right, y2), font_poppins_32)
    if berikutnya:
        row = berikutnya[slide_index_berikutnya % len(berikutnya)]
        nama, kegiatan, start, end, penanggung = row
        waktu_str = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        if kegiatan == "Mata Kuliah":
            labels = ["Mata Kuliah", "Waktu", "Dosen", "Kelas"]
            penanggung_split = penanggung.split("(")
            dosen = penanggung_split[0].strip()
            kelas = penanggung_split[1].replace(")", "").strip() if len(penanggung_split) > 1 else "-"
            values = [nama, waktu_str, dosen, kelas]
        else:
            labels = ["Peminjam", "Kegiatan", "Waktu", "Penanggung Jawab"]
            values = [nama, kegiatan, waktu_str, penanggung]

        y_offset = y2 + 50
        for label, value in zip(labels, values):
            x_label, x_colon, x_value = x_right, x_right + 170, x_right + 185
            if label == "Penanggung Jawab":
                img = draw_text(img, "Penanggung", (x_label, y_offset), font_poppins_24)
                img = draw_text(img, ":", (x_colon, y_offset), font_poppins_24)
                img = draw_text(img, value, (x_value, y_offset), font_poppins_24)
                y_offset += int(font_poppins_24.size * 0.9)
                img = draw_text(img, "Jawab", (x_label, y_offset), font_poppins_24)
                y_offset += int(font_poppins_24.size * 1.2)
            else:
                img = draw_text(img, label, (x_label, y_offset), font_poppins_24)
                img = draw_text(img, ":", (x_colon, y_offset), font_poppins_24)
                img = draw_text(img, value, (x_value, y_offset), font_poppins_24)
                y_offset += int(font_poppins_24.size * 0.9) + 10
    else:
        img = draw_text(img, "Tidak ada jadwal berikutnya", (x_right, y2 + 40), font_poppins_24, color=(180, 180, 180))

    return img

# -------------------------------
# MAIN LOOP
# -------------------------------
cv2.namedWindow("Panel RTF.IV.4", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Panel RTF.IV.4", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

slide_start_time = time_module.time()
slide_index_selesai = 0
slide_index_berikutnya = 0

try:
    encodings_data = load_encodings()

    while True:
        now = time_module.time()
        if now - slide_start_time >= 5:
            slide_index_selesai += 1
            slide_index_berikutnya += 1
            slide_start_time = now

        # Panel utama
        panel = tampilkan_panel(slide_index_selesai, slide_index_berikutnya)
        cv2.imshow("Panel RTF.IV.4", panel)

        key = cv2.waitKey(500) & 0xFF

        if key == ord('k'):
            nama = run_camera(encodings_data)
            if nama:
                konfirmasi_dan_insert(nama)
        elif key == 27:
            break

except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
