const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebarlaboran2Controller');

router.get('/', controller.getJadwal);
router.post('/add', controller.addJadwal);
router.post('/update', controller.updateJadwal);
router.post('/delete', controller.deleteJadwal);

module.exports = router;
