const oracledb = require("oracledb");
const { getPool } = require("../../config/db");

async function findAll() {
    const pool = getPool();
    const connection = await pool.getConnection();

    try {
        const result = await connection.execute(
            `
            SELECT
                "part_id" AS "partId",
                "category" AS "category",
                "brand" AS "brand",
                "part_name" AS "partName",
                "price" AS "price",
                "is_discontinued" AS "isDiscontinued",
                "image_url" AS "imageUrl",
                "product_url" AS "productUrl"
            FROM PARTS
            ORDER BY "part_id"
            `,
            [],
            {
                outFormat: oracledb.OUT_FORMAT_OBJECT
            }
        );

        return result.rows;
    } finally {
        await connection.close();
    }
}

module.exports = {
    findAll
};