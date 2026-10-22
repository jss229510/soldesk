package com.comcheck.comcheck.domain.build;

import java.util.Locale;

public record RecommendationRule (
    String cpuMinLevel,
    int ramMinGb,
    int ssdMinGb,
    boolean requiresDiscreteGpu,
    String gpuMinTier,
    int minVramGb) {

    public static RecommendationRule find(
        String usageType,
        String tierCode) {

        if (usageType == null || usageType.isBlank()
                || tierCode == null || tierCode.isBlank()){
            throw new IllegalArgumentException(
                "용도와 세부등급이 필요합니다.");
        }
        
        String key = usageType.trim()
                .toUpperCase(Locale.ROOT)
                + "/" + tierCode.trim();

        return switch (key) {
            case "OFFICE/ENTRY" -> 
                new RecommendationRule(
                    "OFFICE", 8, 512,
                false, null, 0);

            case "OFFICE/STANDARD" ->
                new RecommendationRule(
                    "OFFICE", 16, 512,
                    false, null, 0);

            case "OFFICE/HEADROOM" ->
                new RecommendationRule(
                    "GAMING", 32, 1000,
                    false, null, 0);

            case "GAMING/FHD_ENTRY" ->
                new RecommendationRule(
                    "GAMING", 16, 1000,
                    true, "중급", 0);

            case "GAMING/QHD_STANDARD" ->
                new RecommendationRule(
                    "GAMING", 32, 1000,
                    true, "고급", 0);

            case "GAMING/FOUR_K_HIGH" ->
                new RecommendationRule(
                    "STREAMING", 32, 2000,
                    true, "최상급", 0);

            case "STREAMING/ENTRY_STREAM" ->
                new RecommendationRule(
                    "STREAMING", 32, 1000,
                    true, "중급", 0);

            case "STREAMING/STANDARD_STREAM" ->
                new RecommendationRule(
                    "STREAMING", 32, 2000,
                    true, "고급", 0);

            case "STREAMING/High_QUALITY_STREAM" ->
                new RecommendationRule(
                    "CREATOR", 64, 2000,
                    true, "최상급", 0);

            case "CREATOR/ENTRY_WORK" ->
                new RecommendationRule(
                    "STREAMING", 32, 1000,
                    true, "중급", 8);

            case "CREATOR/STANDARD_WORK" ->
                new RecommendationRule(
                    "CREATOR", 64, 2000,
                    true, "고급", 12);

            case "CREATOR/HIGH_PERFORMANCE_WORK" ->
                new RecommendationRule(
                    "CREATOR", 64, 4000,
                    true, "최상급", 16);

            default -> throw new IllegalArgumentException(
                        "존재하지 않는 추천 프로필: " + key);
            
        
            };
        }
    }   

