const express = require('express');
const router = express.Router();
const authController = require('../../controllers/authController');

router.get('/', authController.logout);

module.exports = router;
