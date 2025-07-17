const bcrypt = require('bcrypt');
const conn = require('../db');

exports.login = (req, res) => {
  const { nama, password, role } = req.body;

  if (!nama || !password || !role) {
    console.log(`[LOGIN] Gagal: input kosong`);
    return res.redirect('/?error=inputkosong');
  }

  console.log(`[LOGIN] Coba login user: ${nama} | Role input: ${role}`);

  conn.query('SELECT * FROM users WHERE nama = ? AND role = ?', [nama, role], (err, results) => {
    if (err) throw err;

    if (results.length === 0) {
      console.log(`[LOGIN] Gagal: user ${nama} tidak ditemukan`);
      return res.redirect('/?error=user');
    }

    const user = results[0];


    bcrypt.compare(password, user.password, (err, isMatch) => {
      if (err) throw err;

      if (!isMatch) {
        console.log(`[LOGIN] Gagal: password salah untuk ${nama}`);
        return res.redirect('/?error=password');
      }

      req.session.user = {
        id: user.id,
        nama: user.nama,
        role: user.role
      };

      console.log(`[LOGIN] Sukses: ${user.role} ${user.nama} login`);
      if (user.role === 'dosen') {
        console.log(`[SAPAAN] Selamat datang Dosen ${user.nama}`);
      }

      // Alihkan ke dashboard role
      res.redirect(`/${user.role}`);
    });
  });
};

exports.logout = (req, res) => {
  if (req.session.user) {
    console.log(`[LOGOUT] ${req.session.user.role} ${req.session.user.nama} logout`);
    req.session.destroy(err => {
      if (err) throw err;
      res.redirect('/');
    });
  } else {
    console.log('[LOGOUT] Tidak ada user login');
    res.redirect('/');
  }
};
