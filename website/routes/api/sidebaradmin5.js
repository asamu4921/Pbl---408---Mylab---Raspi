const express = require('express');
const router = express.Router();
const controller = require('../../controllers/sidebaradmin5Controller');

router.get('/', controller.getUsers);

module.exports = router;
