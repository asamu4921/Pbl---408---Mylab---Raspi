const mysql = require('mysql2');
const conn = mysql.createConnection({
  host: 'localhost',
  user: 'pbl408',
  password: 'gpuasamu',
  database: 'mylab'
});

conn.connect(err => {
  if (err) throw err;
  console.log('Tersambung ke database MySQL.');
});

module.exports = conn;
