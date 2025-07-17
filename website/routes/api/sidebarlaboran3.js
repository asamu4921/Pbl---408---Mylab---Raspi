const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebarlaboran3Controller');

// Pastikan user sudah login laboran (kalau kamu mau middleware, silakan tambah)
router.get('/', controller.getAktivitasLab);
router.post('/add', controller.addAktivitasLab);
router.post('/update', controller.updateAktivitasLab);
router.post('/delete', controller.deleteAktivitasLab);

module.exports = router;
