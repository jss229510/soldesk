import { request } from "./client";

export async function getReplacementCandidates({
    usageType,
    tierCode,
    category,
    items}, { signal } = {}) {

    const candidates = await request('/build/replacements', {
        method: 'POST',
        signal,
        body: JSON.stringify({
            usageType,
            tierCode,
            category,
            items: items.map((item)=>({
                partId: item.part.id,
                quantity: item.quantity ?? 1,
            }))
        })
    });
    if(!Array.isArray(candidates) || candidates.some((candidate)=>!candidate?.part.id)){
        throw new Error('교체 후보 응답 형식이 올바르지 않습니다.');
    }
    return candidates;
}