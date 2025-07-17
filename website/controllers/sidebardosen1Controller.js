const conn = require('../db');

exports.getAktivitasRuangDosen = (req, res) => {
  const namaLogin = req.session.user.nama;

  // GRUP 1: hanif, naurah, kavit
  const grup1 = ['hanif', 'naurah', 'kavit'];

  // GRUP 2: uruguai, argentina, indonesia
  const grup2 = ['uruguai', 'argentina', 'indonesia'];

  let filterNama = [];

  if (grup1.includes(namaLogin)) {
    filterNama = grup1;
  } else if (grup2.includes(namaLogin)) {
    filterNama = grup2;
  } else {
    // Kalau bukan bagian grup manapun, hanya data dirinya
    filterNama = [namaLogin];
  }

  const tanggal = req.query.tanggal;

  let sql = 'SELECT * FROM aktivitas_ruang_dosen WHERE nama_dosen IN (?)';
  const params = [filterNama];

  if (tanggal) {
    sql += ' AND DATE(datetime) = ?';
    params.push(tanggal);
    console.log(`[SIDEBAR1] User ${namaLogin} filter tanggal: ${tanggal}`);
  }

  console.log(`[SIDEBAR1] User ${namaLogin} akses. Filter: ${filterNama.join(', ')}`);

  conn.query(sql, params, (err, results) => {
    if (err) throw err;

    console.log(`[SIDEBAR1] Dapat ${results.length} baris`);
    res.json(results);
  });
};
