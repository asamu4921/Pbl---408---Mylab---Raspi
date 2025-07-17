const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebaradmin2Controller');

router.get('/', controller.getJadwal);
router.get('/ruangan', controller.getRuanganList);

module.exports = router;
