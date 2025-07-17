const conn = require('../db');

exports.getAktivitasLab = (req, res) => {
  const kode = req.query.kode_ruangan;

  const mapping = {
    'iguana': 'RTF.IV.4',
    'sule': 'RTF.IV.2',
    'samurai': 'RTF.IV.1',
    'uriel': 'RTF.III.6',
    'polnarev': 'GU 601',
    'Banu Failasuf, S.Tr': 'GU 805',
    'Agus Riady, A.Md.Kom': 'GU 705',
    'Supardianto, S.ST.M.Eng.': 'RTF.V.1',
    'Sartikha, S. ST., M.Eng': 'TA.XII.4'
  };

  let laboranList = [];

  if (!kode) {
    // Kalau user pilih "Semua Ruangan" => hanya laboran yang ada di mapping
    laboranList = Object.keys(mapping);
  } else {
    // Cari nama laboran yang match dengan kode ruangan
    for (const [nama, ruangan] of Object.entries(mapping)) {
      if (ruangan === kode) laboranList.push(nama);
    }

    if (laboranList.length === 0) {
      return res.json({ rows: [] }); // Kalau tidak ada yg cocok
    }
  }

  const sql = `SELECT * FROM aktivitas_ruang_lab WHERE nama_laboran IN (?)`;
  conn.query(sql, [laboranList], (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'DB ERROR' });
    }
    res.json({ rows });
  });
};

exports.getRuangan = (req, res) => {
  conn.query('SELECT DISTINCT kode_ruangan, nama_ruangan FROM api ORDER BY kode_ruangan', (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'DB ERROR' });
    }
    res.json(rows);
  });
};
