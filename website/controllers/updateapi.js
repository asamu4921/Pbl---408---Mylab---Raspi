const mysql = require('mysql2');
const fetch = (...args) =>
  import('node-fetch').then(({ default: fetch }) => fetch(...args));

const conn = require('../db'); // Pake koneksi globalmu

exports.updateAPI = async (req, res) => {
  const apiUrl = 'https://peminjaman.polibatam.ac.id/api-penru/data-peminjaman';
  const apiKey = '9a89a3be-1d44-4e81-96a8-585cb0453718';

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: { 'api-key': apiKey }
    });

    const data = await response.json();

    if (!Array.isArray(data)) {
      console.error('[x] Data API tidak valid atau kosong.');
      return res.status(500).json({ message: 'Data API tidak valid' });
    }

    console.log(`[i] Jumlah data diterima dari API: ${data.length}`);

    // Simpan ke DB
    simpanKeDatabase(data, res);

  } catch (err) {
    console.error('[x] Gagal ambil data dari API:', err);
    return res.status(500).json({ message: 'Gagal ambil data dari API' });
  }
};

// Proses 1 per 1
function simpanKeDatabase(dataList, res) {
  let index = 0;
  let berhasil = 0;

  function prosesSatuPerSatu() {
    if (index >= dataList.length) {
      console.log(`[✓] Proses selesai. Total data baru disimpan: ${berhasil}`);
      return res.json({ message: `Proses selesai. Data baru disimpan: ${berhasil}` });
    }

    const item = dataList[index++];
    const {
      nim_mahasiswa, nama_mahasiswa, jenis_kegiatan, nama_kegiatan_other,
      tanggal_pinjam, start_time, end_time, kode_ruangan,
      nama_ruangan, gedung_ruangan, nik_penanggungjawab, nama_penanggungjawab
    } = item;

    const cekQuery = `
      SELECT id FROM api WHERE nim_mahasiswa = ? AND tanggal_pinjam = ? AND start_time = ?
    `;

    conn.query(cekQuery, [nim_mahasiswa, tanggal_pinjam, start_time], (cekErr, rows) => {
      if (cekErr) {
        console.error('[x] Gagal cek duplikat:', cekErr);
        return prosesSatuPerSatu();
      }

      if (rows.length > 0) {
        console.log(`[!] Duplikat dilewati: ${nim_mahasiswa} (${tanggal_pinjam} ${start_time})`);
        return prosesSatuPerSatu();
      }

      const insertQuery = `
        INSERT INTO api (
          nim_mahasiswa, nama_mahasiswa, jenis_kegiatan,
          nama_kegiatan_other, tanggal_pinjam, start_time, end_time,
          kode_ruangan, nama_ruangan, gedung_ruangan,
          nik_penanggungjawab, nama_penanggungjawab
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `;

      conn.query(insertQuery, [
        nim_mahasiswa, nama_mahasiswa, jenis_kegiatan,
        nama_kegiatan_other, tanggal_pinjam, start_time, end_time,
        kode_ruangan, nama_ruangan, gedung_ruangan,
        nik_penanggungjawab, nama_penanggungjawab
      ], (insertErr) => {
        if (insertErr) {
          console.error(`[x] Gagal insert: ${nim_mahasiswa} (${tanggal_pinjam})`, insertErr);
        } else {
          console.log(`[✓] Data disimpan: ${nim_mahasiswa} (${tanggal_pinjam} ${start_time})`);
          berhasil++;
        }
        prosesSatuPerSatu();
      });
    });
  }

  prosesSatuPerSatu();
}
