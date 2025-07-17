const conn = require('../db');

exports.getUsers = (req, res) => {
  const role = req.query.role;

  let sql = `SELECT * FROM users`;
  const params = [];

  if (role && role !== 'all') {
    sql += ` WHERE role = ?`;
    params.push(role);
  }

  conn.query(sql, params, (err, rows) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: 'DB ERROR' });
    }
    res.json(rows);
  });
};
