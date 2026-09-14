const oracledb = require("oracledb");
const dotenv = require("dotenv");
dotenv.config();

const poolConfig = {
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    connectString: process.env.DB_CONNECT_STRING,
    poolMin: 1,
    poolMax: 5,
    poolIncrement: 1
}

let pool;

async function connectDB() {
    try {
        pool = await oracledb.createPool(poolConfig);
        console.log("Oracle DB연결 성공");
        return pool;
    } catch (error) {
        console.error("Oracle DB연결 실패: ", error);
        return error;
    }
}

function getPool() {
    return pool;
}

module.exports = {
    connectDB,
    getPool
};