const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebardosen1Controller');

router.get('/', controller.getAktivitasRuangDosen);

module.exports = router;
