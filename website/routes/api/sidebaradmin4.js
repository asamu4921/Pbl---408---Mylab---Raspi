const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebaradmin4Controller');

router.get('/', controller.getAktivitasLab);
router.get('/ruangan', controller.getRuangan);

module.exports = router;
