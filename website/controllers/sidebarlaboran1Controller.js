const conn = require('../db');

// Ambil pinjaman (dengan filter kode_ruangan)
exports.getPinjaman = (req, res) => {
  const kode = req.query.kode_ruangan;
  let sql = 'SELECT * FROM api';
  let params = [];

  if (kode) {
    sql += ' WHERE kode_ruangan = ?';
    params.push(kode);
  }

  conn.query(sql, params, (err, rows) => {
    if (err) throw err;
    res.json(rows);
  });
};

// Ambil list unik kode_ruangan
exports.getListRuangan = (req, res) => {
  conn.query('SELECT DISTINCT kode_ruangan, nama_ruangan FROM api ORDER BY kode_ruangan', (err, rows) => {
    if (err) throw err;
    res.json(rows);
  });
};
