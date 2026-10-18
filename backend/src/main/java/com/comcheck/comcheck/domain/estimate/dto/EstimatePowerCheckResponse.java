package com.comcheck.comcheck.domain.estimate.dto;

// 전력 호환성 검사 결과 응답 DTO
// 프론트는 compatible(true/false)로 경고 표시 여부

public record EstimatePowerCheckResponse(

        Long estimatedId, // 견적번호
        Long cpuTdp, // CPU 소비전력 합계 //part_specs_all.csv에 tdp
        Long gpuTdp, // GPU 소비전력 합계
        Long totalPower, // CPU + GPU 소비전력 합계
        Long psuWattage, // 견적에 담긴 파워의 정격출력 (W)
        Long requiredWattage, // 이 견적에 필요한 최소 파워 출력
        String status, // OK, INSUFFICIENT, NO_PSU, UNKNOWN 중 하나
        boolean compatible, // status가 OK일 때만 true
        String message // 사용자에게 보여줄 설명

) {
    
    public static final String OK = "OK"; // 파워 출력이 충분함
    public static final String INSUFFICIENT = "INSUFFICIENT"; // 파워 출력이 부족함
    public static final String NO_PSU = "NO_PSU"; // 견적에 파워가 없음
    public static final String UNKNOWN = "UNKNOWN"; // 스펙 데이터가 없어 판단 불가

}
