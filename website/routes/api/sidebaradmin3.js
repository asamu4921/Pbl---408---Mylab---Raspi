const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebaradmin3Controller');

router.get('/', controller.getAktivitasDosen);

module.exports = router;
