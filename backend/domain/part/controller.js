const service = require("./service");

async function getParts(req, res) {
    try {
        const parts = await service.getParts();

        res.json(parts);
    } catch (error){
        console.error("부품 조회 실패: ", error);

        res.status(500).json({
            message: "부품 조회 실패"
        });
    }
}

module.exports = {
    getParts
};