const express = require("express");
const cors = require("cors");
const {connectDB} = require("./config/db");

const app = express();

const partRouter = require("./domain/part/router");

// cors() → React 프론트에서 API 요청 가능
// express.json() → JSON 형태의 요청 데이터를 읽을 수 있게 함

app.use(cors());
app.use("/api/parts", partRouter);

connectDB();

app.get("/", (req,res) => {
    res.json({message: "PC 부품 추천 서비스 API"});
});

module.exports =app;