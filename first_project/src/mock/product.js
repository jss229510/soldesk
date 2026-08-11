const now = Date.now();
const hours = (n) => new Date(now+n*60*60*1000).toISOString();
const days = (n) => new Date(now+n*24*60*60*1000).toISOString();

export const PRODUCTS = [
    {
        id: "p1",
        name: "라이젠 7 7800X3D",
        category: "cpu",
        icon: "cpu",
        currentBid: 385000,
        buyNowPrice: null,
        deadline: hours(2.24),
        bidCount: 12,
        compatVerified: true
    },
    {
        id: "p2",
        name: "RTX 4070 Super",
        category: "gpu",
        icon: "device-desktop",
        currentBid: 720000,
        buyNowPrice: null,
        deadline: days(1.14),
        bidCount: 5,
        compatVerified: false
    },
    {
        id: "p3",
        name: "750W 80+ 골드 파워",
        category: "psu",
        icon: "bolt",
        currentBid: null,
        buyNowPrice: 98000,
        deadline: days(5),
        bidCount: 0,
        compatVerified: false
    }
]