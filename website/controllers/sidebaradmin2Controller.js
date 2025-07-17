// controllers/sidebaradmin2Controller.js
const conn = require('../db');

exports.getJadwal = (req, res) => {
  const kodeRuangan = req.query.kode_ruangan || '';

  let sql = 'SELECT * FROM jadwal_matkul';
  const params = [];

  if (kodeRuangan) {
    sql += ' WHERE kode_ruangan = ?';
    params.push(kodeRuangan);
  }

  conn.query(sql, params, (err, results) => {
    if (err) throw err;
    res.json(results);
  });
};

exports.getRuanganList = (req, res) => {
  conn.query(
    'SELECT DISTINCT kode_ruangan, nama_ruangan FROM api ORDER BY kode_ruangan',
    (err, results) => {
      if (err) throw err;
      res.json(results);
    }
  );
};
