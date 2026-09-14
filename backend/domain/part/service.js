const repository = require("./repository");
async function getParts() {
    return await repository.findAll();
}

module.exports = {
    getParts
};