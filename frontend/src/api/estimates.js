//api/estimates.js -- 견적 조회·저장 요청 함수

import { PC_BUILD_PROFILES } from "../constants/usages";
//checkCompatibility: pc부품들의 호환성을 검사하는 함수
import { checkCompatibility } from "../utils/compatibility";
import { USE_MOCK } from "./client";

//reduce(): 배열의 요소를 하나씩 처리하는 함수
const summarize = (items) => {
    const total = items.reduce((sum, item) => sum + item.part.price, 0);

    return {
        items,
        total,
        compatibility: checkCompatibility(items),
    };
};

// 용도별 추천 견적 조회
export async function getRecommendEstimates(usageType, tierCode) {
    if (!usageType || !tierCode) {
        throw new Error("용도와 등급을 선택해주세요.")
    }

    if (!USE_MOCK) {
        const params = new URLSearchParams({ usageType, tierCode });

        const res = await fetch(`/builds/presets/${usageType}?${params}`);

        if (!res.ok) {
            throw new Error("추천 견적을 불러오지 못했습니다.");
        }
        return res.json();
    }
    const preset = PC_BUILD_PROFILES.find(
        (p) => p.id === usageType
    ) ?? null;

    if (!preset) {
        throw new Error("해당 용도를 찾을 수 없습니다.");
    }

    // 선택한 등급 찾기
    const tier = preset.tiers.find(
        (t) => t.code === tierCode
    );

    // 현재 선택한 프리셋 정보 반환
    return {
        usageType,
        tierCode,
        preset,
        tier,
        items: [],
    };
}

// 용도 프리셋 목록
export async function getUsagePresets() {
    return { presets: PC_BUILD_PROFILES }
}