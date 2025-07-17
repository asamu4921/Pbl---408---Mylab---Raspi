const conn = require('../db');

exports.getJadwal = (req, res) => {
  const namaLogin = req.session.user.nama;
  const ruanganMap = {
  'Ahmad Saif Almuflihin': 'RTF.IV.4',
  'sule': 'RTF.IV.2',
  'samurai': 'RTF.IV.1',
  'uriel': 'RTF.III.6',
  'polnarev': 'GU 601',
};
  const kodeRuangan = ruanganMap[namaLogin];

  const hari = req.query.hari;

  let sql = 'SELECT * FROM jadwal_matkul WHERE kode_ruangan = ?';
  let params = [kodeRuangan];

  if (hari) {
    sql += ' AND hari = ?';
    params.push(hari);
  }

  conn.query(sql, params, (err, results) => {
    if (err) throw err;
    res.json(results);
  });
};


exports.addJadwal = (req, res) => {
  const namaLogin = req.session.user.nama;

  const aksesRuangan = {
  'Ahmad Saif Almuflihin': 'RTF.IV.4',
  'sule': 'RTF.IV.2',
  'samurai': 'RTF.IV.1',
  'uriel': 'RTF.III.6',
  'polnarev': 'GU 601',
};

  const kodeRuangan = aksesRuangan[namaLogin] || '';

  const { matkul, start_time, end_time, kelas, dosen, hari } = req.body;

  conn.query(
    'INSERT INTO jadwal_matkul (matkul, start_time, end_time, kode_ruangan, kelas, dosen, hari) VALUES (?, ?, ?, ?, ?, ?, ?)',
    [matkul, start_time, end_time, kodeRuangan, kelas, dosen, hari],
    (err) => {
      if (err) throw err;
      res.json({ message: 'Data jadwal ditambahkan' });
    }
  );
};

exports.updateJadwal = (req, res) => {
  const { id, matkul, start_time, end_time, kelas, dosen, hari } = req.body;

  conn.query(
    'UPDATE jadwal_matkul SET matkul = ?, start_time = ?, end_time = ?, kelas = ?, dosen = ?, hari = ? WHERE id = ?',
    [matkul, start_time, end_time, kelas, dosen, hari, id],
    (err) => {
      if (err) throw err;
      res.json({ message: 'Data jadwal diperbarui' });
    }
  );
};

exports.deleteJadwal = (req, res) => {
  const { id } = req.body;

  conn.query(
    'DELETE FROM jadwal_matkul WHERE id = ?',
    [id],
    (err) => {
      if (err) throw err;
      res.json({ message: 'Data jadwal dihapus' });
    }
  );
};
