const express = require('express');
const session = require('express-session');
const loginRoutes = require('./routes/auth/login');
const logoutRoutes = require('./routes/auth/logout');
const logger = require('./middleware/logger');
const path = require('path');
const sidebarDosen1Routes = require('./routes/api/sidebardosen1');
const sidebarDosen2Routes = require('./routes/api/sidebardosen2');
const sidebarLaboran1Routes = require('./routes/api/sidebarlaboran1');
const sidebarLaboran2Routes = require('./routes/api/sidebarlaboran2');
const sidebarLaboran3Routes = require('./routes/api/sidebarlaboran3');
const sidebarLaboran4Routes = require('./routes/api/sidebarlaboran4');
const updateAPIRoutes = require('./routes/api/updateapi');
const sidebarAdmin2Routes = require('./routes/api/sidebaradmin2');
// Kalau nanti Sidebar 3–7 juga pakai route terpisah:
const sidebarAdmin3Routes = require('./routes/api/sidebaradmin3');
const sidebarAdmin4Routes = require('./routes/api/sidebaradmin4');
const sidebarAdmin5Routes = require('./routes/api/sidebaradmin5');
// const sidebarAdmin6Routes = require('./routes/api/sidebaradmin6');
// const sidebarAdmin7Routes = require('./routes/api/sidebaradmin7');


const app = express(); // 👈 HARUS DI ATAS sebelum pakai `app.use`

app.use(express.json());
app.use(express.urlencoded({ extended: true })); // <-- WAJIB buat form HTML biasa
app.use(session({
  secret: 'rahasia_mantap',
  resave: false,
  saveUninitialized: true
}));
// sidebar routes
app.use('/api/sidebardosen1', sidebarDosen1Routes);
app.use('/api/sidebardosen2', sidebarDosen2Routes);
app.use('/api/sidebarlaboran1', sidebarLaboran1Routes);
app.use('/api/sidebarlaboran2', sidebarLaboran2Routes);
app.use('/api/sidebarlaboran3', sidebarLaboran3Routes);
app.use('/api/sidebarlaboran4', sidebarLaboran4Routes);
app.use('/api/updateapi', updateAPIRoutes);
app.use('/api/admin/sidebar2', sidebarAdmin2Routes);
// Kalau nanti Sidebar 3–7 pakai controller & route juga:
app.use('/api/admin/sidebar3', sidebarAdmin3Routes);
app.use('/api/admin/sidebar4', sidebarAdmin4Routes);
app.use('/api/admin/sidebar5', sidebarAdmin5Routes);
// app.use('/api/admin/sidebar6', sidebarAdmin6Routes);
// app.use('/api/admin/sidebar7', sidebarAdmin7Routes);


// Logger global
app.use(logger);

// Layani file statis dari folder views (kalau mau ada gambar, CSS, dll)
app.use(express.static(path.join(__dirname, 'views')));

// Root `/` kirim login.html — TIDAK BOLEH DUA KALI!
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'login.html'));
});
app.get('/dosen', (req, res) => {
  if (!req.session.user || req.session.user.role !== 'dosen') {
    return res.redirect('/');
  }
  res.sendFile(path.join(__dirname, 'views', 'dosen.html'));
});

app.get('/laboran', (req, res) => {
  if (!req.session.user || req.session.user.role !== 'laboran') {
    return res.redirect('/');
  }
  res.sendFile(path.join(__dirname, 'views', 'laboran.html'));
});

app.get('/superadmin', (req, res) => {
  if (!req.session.user || req.session.user.role !== 'superadmin') {
    return res.redirect('/');
  }
  res.sendFile(path.join(__dirname, 'views', 'admin.html'));
});
app.get('/api/me', (req, res) => {
  if (!req.session.user) return res.status(401).json({ error: 'Unauthorized' });
  res.json({ nama: req.session.user.nama, role: req.session.user.role });
});


app.use('/login', loginRoutes);
app.use('/logout', logoutRoutes);

app.listen(3000, () => {
  console.log('Server jalan di http://localhost:3000');
});
