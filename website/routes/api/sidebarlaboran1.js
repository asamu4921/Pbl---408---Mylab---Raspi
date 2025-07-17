const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebarlaboran1Controller');

router.get('/', controller.getPinjaman);
router.get('/ruangan', controller.getListRuangan);

module.exports = router;
