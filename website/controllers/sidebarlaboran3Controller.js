const conn = require('../db');

exports.getAktivitasLab = (req, res) => {
  const namaLaboran = req.session.user.nama;

  conn.query(
    'SELECT * FROM aktivitas_ruang_lab WHERE nama_laboran = ? ORDER BY datetime DESC',
    [namaLaboran],
    (err, results) => {
      if (err) throw err;
      res.json(results);
    }
  );
};

exports.addAktivitasLab = (req, res) => {
  const namaLaboran = req.session.user.nama;
  const { status } = req.body;

  const datetime = new Date(); // Sekarang

  conn.query(
    'INSERT INTO aktivitas_ruang_lab (nama_laboran, datetime, status) VALUES (?, ?, ?)',
    [namaLaboran, datetime, status],
    (err, result) => {
      if (err) throw err;
      res.json({ success: true });
    }
  );
};

exports.updateAktivitasLab = (req, res) => {
  const { id, status } = req.body;

  conn.query(
    'UPDATE aktivitas_ruang_lab SET status = ? WHERE id = ?',
    [status, id],
    (err, result) => {
      if (err) throw err;
      res.json({ success: true });
    }
  );
};

exports.deleteAktivitasLab = (req, res) => {
  const { id } = req.body;

  conn.query(
    'DELETE FROM aktivitas_ruang_lab WHERE id = ?',
    [id],
    (err, result) => {
      if (err) throw err;
      res.json({ success: true });
    }
  );
};
