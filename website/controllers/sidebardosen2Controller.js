const conn = require('../db');

// Ambil aktivitas diri sendiri (opsional filter tanggal)
exports.getAktivitasDiriSendiri = (req, res) => {
  const user = req.session.user;
  const tanggal = req.query.tanggal;

  let sql = 'SELECT * FROM aktivitas_ruang_dosen WHERE nama_dosen = ?';
  const params = [user.nama];

  if (tanggal && tanggal !== 'all') {
    sql += ' AND DATE(datetime) = ?';
    params.push(tanggal);
    console.log(`[SIDEBAR2] ${user.nama} lihat aktivitas | Filter tanggal: ${tanggal}`);
  } else {
    console.log(`[SIDEBAR2] ${user.nama} lihat aktivitas | Filter tanggal: Semua`);
  }

  conn.query(sql, params, (err, rows) => {
    if (err) throw err;
    res.json(rows);
  });
};


// Tambah aktivitas diri sendiri
exports.addAktivitas = (req, res) => {
  const namaLogin = req.session.user.nama;
  const { status } = req.body;

  if (!status) {
    return res.status(400).json({ message: 'Status wajib diisi' });
  }

  conn.query(
    'INSERT INTO aktivitas_ruang_dosen (nama_dosen, datetime, status) VALUES (?, NOW(), ?)',
    [namaLogin, status],
    (err, result) => {
      if (err) throw err;
      console.log(`[SIDEBAR2] ${namaLogin} tambah aktivitas (datetime: NOW())`);
      res.json({ message: 'Aktivitas ditambah', id: result.insertId });
    }
  );
};


// Update aktivitas diri sendiri
exports.updateAktivitas = (req, res) => {
  const namaLogin = req.session.user.nama;
  const { id, status } = req.body;

  conn.query(
    'UPDATE aktivitas_ruang_dosen SET status = ? WHERE id = ? AND nama_dosen = ?',
    [status, id, namaLogin],
    (err, result) => {
      if (err) throw err;
      console.log(`[SIDEBAR2] ${namaLogin} update aktivitas ID ${id}`);
      res.json({ message: 'Aktivitas diperbarui' });
    }
  );
};


// Hapus aktivitas diri sendiri
exports.deleteAktivitas = (req, res) => {
  const namaLogin = req.session.user.nama;
  const { id } = req.body;

  conn.query(
    'DELETE FROM aktivitas_ruang_dosen WHERE id = ? AND nama_dosen = ?',
    [id, namaLogin],
    (err, result) => {
      if (err) throw err;
      console.log(`[SIDEBAR2] ${namaLogin} hapus aktivitas ID ${id}`);
      res.json({ message: 'Aktivitas dihapus' });
    }
  );
};
