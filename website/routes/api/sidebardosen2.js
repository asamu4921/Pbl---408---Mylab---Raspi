const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebardosen2Controller');

router.get('/', controller.getAktivitasDiriSendiri);
router.post('/add', controller.addAktivitas);
router.post('/update', controller.updateAktivitas);
router.post('/delete', controller.deleteAktivitas);

module.exports = router;
