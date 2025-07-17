const express = require('express');
const router = express.Router();
const controller = require('../../controllers/updateapi');

router.get('/updateapi', controller.updateAPI);

module.exports = router;
