module.exports = (req, res, next) => {
  const waktu = new Date().toISOString();
  const method = req.method;
  const url = req.originalUrl;

  // Kalau ada user yang login di session
  const user = req.session && req.session.user 
    ? `[${req.session.user.role}] ${req.session.user.nama}` 
    : 'Anonymous';

  console.log(`[${waktu}] ${method} ${url} | User: ${user}`);

  next();
};
