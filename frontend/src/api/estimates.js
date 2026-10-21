//api/estimates.js -- 견적 조회·저장 요청 함수

import { PC_BUILD_PROFILES } from "../constants/usages";
import { request } from "./client";

// 용도별 추천 견적 조회
export async function getRecommendEstimates(
    usageType,
    tierCode
) {
    if (!usageType || !tierCode) {
        throw new Error("용도와 등급을 선택해주세요.");
    }

    const params = new URLSearchParams({
        usageType,
        tierCode,
        page: "0",
        size: "1",
    });

    const result = await request(
        `/estimates/recommended?${params}`
    );

    if (!Array.isArray(result?.estimates)) {
        throw new Error("추천 응답 형식이 올바르지 않습니다.");
    }

    const estimate = result.estimates[0];

    if (!estimate) {
        throw new Error("해당 조건의 추천 견적이 없습니다.");
    }

    if (result.totalElements > 1) {
        throw new Error(
            "추천 견적이 여러 건입니다. 선택 기준을 확인해주세요."
        );
    }

    const items = await request(
        `/estimates/${estimate.estimatedId}/items`
    );

    if (!Array.isArray(items)) {
        throw new Error("품목 응답 형식이 올바르지 않습니다.");
    }

    return {
        ...estimate,
        items: items.map((item) => ({
            itemId: item.itemId,
            category: item.category?.toLowerCase(),
            quantity: item.quantity,
            itemPrice: item.itemPrice,
            part: {
                id: item.partId,
                name: item.partName,
                price: item.unitPrice,
                imageUrl: item.imageUrl,
                productUrl: item.productUrl,
            },
        })),
    };
}

// 용도 프리셋 목록
export async function getUsagePresets() {
    return { presets: PC_BUILD_PROFILES }
}