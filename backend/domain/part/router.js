const express = require("express");
const controller = require("./controller");

const router = express.Router();
router.get("/", controller.getParts);

module.exports = router;


// 백엔드 실행 순서
// /api/parts
//     ↓
// router.js
//     ↓
// controller.js
//     ↓
// service.js
//     ↓
// repository.js
//     ↓
// Oracle PARTS