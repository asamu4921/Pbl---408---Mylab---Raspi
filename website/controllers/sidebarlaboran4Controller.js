const conn = require('../db');

exports.getRuangLab = (req, res) => {
  const namaLaboran = req.session.user.nama;

  let kodeRuangan = '';
  if (namaLaboran === 'Ahmad Saif Almuflihin') kodeRuangan = 'RTF.IV.4';
  else if (namaLaboran === 'sule') kodeRuangan = 'RTF.IV.2';
  else if (namaLaboran === 'samurai') kodeRuangan = 'RTF.IV.1';
  else if (namaLaboran === 'uriel') kodeRuangan = 'RTF.III.6';

  const now = new Date();
  const today = now.toISOString().split('T')[0]; // yyyy-mm-dd

  const namaHari = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
  const hariIni = namaHari[now.getDay()]; // Sesuai DB-mu: Senin, Selasa, dst.

  // Pinjaman hari ini
  const q1 = new Promise((resolve, reject) => {
    conn.query(
      'SELECT * FROM api WHERE kode_ruangan = ? AND tanggal_pinjam = ? ORDER BY start_time',
      [kodeRuangan, today],
      (err, result) => {
        if (err) reject(err);
        else resolve(result);
      }
    );
  });

  // Jadwal matkul hari ini
  const q2 = new Promise((resolve, reject) => {
    conn.query(
      'SELECT * FROM jadwal_matkul WHERE kode_ruangan = ? AND hari = ? ORDER BY start_time',
      [kodeRuangan, hariIni],
      (err, result) => {
        if (err) reject(err);
        else resolve(result);
      }
    );
  });

  Promise.all([q1, q2])
    .then(([apiData, jadwalData]) => {
      res.json({
        api: apiData,
        jadwal: jadwalData,
        kode_ruangan: kodeRuangan,
        tanggal: today,
        hari: hariIni
      });
    })
    .catch(err => {
      console.error(err);
      res.status(500).json({ error: 'Gagal ambil data' });
    });
};
