const conn = require('../db');

exports.getAktivitasDosen = (req, res) => {
  const grup1 = ['hanif', 'naurah', 'kavit'];
  const grup2 = ['uruguai', 'argentina', 'indonesia'];

  conn.query('SELECT * FROM aktivitas_ruang_dosen', (err, results) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'DB ERROR' });
    }

    // Pastikan nama_dosen jadi lowercase dulu supaya match
    const g1 = results.filter(r => grup1.includes(r.nama_dosen.toLowerCase()));
    const g2 = results.filter(r => grup2.includes(r.nama_dosen.toLowerCase()));

    res.json({ grup1: g1, grup2: g2 });
  });
};
