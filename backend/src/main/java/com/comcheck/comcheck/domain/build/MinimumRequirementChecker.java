package com.comcheck.comcheck.domain.build;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public final class MinimumRequirementChecker {

    private static final Map<String, Integer> CPU_LEVELS = 
        Map.of(
                "OFFICE", 1,
                "GAMING", 2,
                "STREAMING", 3,
                "CREATOR", 4
        );
    
    private static final Map<String, Integer> GPU_LEVELS = 
        Map.of(
                "보급", 1,
                "중급", 2,
                "고급", 3,
                "최상급", 4 
        );

     private MinimumRequirementChecker() {
    }

    public record Result(List<String> reasons) {

        public Result {
            reasons = List.copyOf(reasons);
        }

        public boolean passed() {
            return reasons.isEmpty();
        }
    }

    public static Result check(
            String usageType,
            String tierCode,
            String category,
            Map<String, String> specs,
            Long quantity) {

        RecommendationRule rule =
                RecommendationRule.find(usageType, tierCode);

        Map<String, String> values =
                specs == null ? Map.of() : specs;

        List<String> reasons = new ArrayList<>();

        switch (normalize(category)) {
            case "CPU" -> checkCpu(rule, values, reasons);
            case "RAM" ->
                checkRam(rule, values, quantity, reasons);
            case "SSD" -> checkSsd(rule, values, reasons);
            case "GPU" -> checkGpu(rule, values, reasons);
            default -> throw new IllegalArgumentException(
                    "최소조건 검사에서 지원하지 않는 부품: "
                            + category);
        }

        return new Result(reasons);
    }

    public static boolean matchesReplacementLevel(
            String category,
            Map<String, String> currentSpecs,
            Map<String, String> candidateSpecs) {

        if (currentSpecs == null || candidateSpecs == null) {
            return false;
        }

        return switch (normalize(category)) {
            case "CPU" -> {
                Integer currentLevel = CPU_LEVELS.get(
                        normalize(currentSpecs.get("cpu_level")));

                Integer candidateLevel = CPU_LEVELS.get(
                        normalize(candidateSpecs.get("cpu_level")));

                yield currentLevel != null
                        && currentLevel.equals(candidateLevel);
            }

            case "GPU" -> {
                int currentLevel = gpuLevel(
                        normalize(currentSpecs.get("chipset")));

                int candidateLevel = gpuLevel(
                        normalize(candidateSpecs.get("chipset")));

                yield currentLevel > 0
                        && currentLevel == candidateLevel;
            }

            case "RAM" -> samePositiveNumber(
                    currentSpecs.get("capacity_gb"),
                    candidateSpecs.get("capacity_gb"));

            case "SSD" -> {
                int currentBand = storageBand(
                        currentSpecs.get("storage_gb"));

                int candidateBand = storageBand(
                        candidateSpecs.get("storage_gb"));

                yield currentBand > 0
                        && currentBand == candidateBand;
            }

            case "MAINBOARD", "PSU" -> true;

            default -> throw new IllegalArgumentException(
                    "교체 등급 비교에서 지원하지 않는 부품: "
                            + category);
        };
    }

    private static boolean samePositiveNumber(
            String currentValue,
            String candidateValue) {

        Double current = positiveNumber(currentValue);
        Double candidate = positiveNumber(candidateValue);

        return current != null && current.equals(candidate);
    }

    private static int storageBand(String value) {
        Double storage = positiveNumber(value);

        if (storage == null) {
            return 0;
        }

        if (storage >= 450 && storage <= 600) {
            return 1;
        }

        if (storage >= 900 && storage <= 1200) {
            return 2;
        }

        if (storage >= 1900 && storage <= 2200) {
            return 3;
        }

        if (storage >= 3900) {
            return 4;
        }

        return 0;
    }
    
    private static void checkCpu(
            RecommendationRule rule,
            Map<String, String> specs,
            List<String> reasons) {

        Integer actual = CPU_LEVELS.get(
                normalize(specs.get("cpu_level")));

        int required = CPU_LEVELS.get(rule.cpuMinLevel());

        if (actual == null) {
            reasons.add(
                    "CPU 등급이 누락되었거나 분류되지 않았습니다.");
        } else if (actual < required) {
            reasons.add("CPU 등급이 최소조건보다 낮습니다.");
        }
    }

    private static void checkRam(
            RecommendationRule rule,
            Map<String, String> specs,
            Long quantity,
            List<String> reasons) {

        Double capacity = positiveNumber(
                specs.get("capacity_gb"));

        if (capacity == null) {
            reasons.add(
                    "RAM 용량이 누락되었거나 유효하지 않습니다.");
        }

        if (quantity == null || quantity < 1) {
            reasons.add("RAM 수량은 양의 정수여야 합니다.");
        } else if (capacity != null
                && capacity * quantity < rule.ramMinGb()) {
            reasons.add("RAM 총용량이 최소조건보다 작습니다.");
        }
    }

    private static void checkSsd(
            RecommendationRule rule,
            Map<String, String> specs,
            List<String> reasons) {

        if (!"M.2".equals(
                normalize(specs.get("form_factor")))) {
            reasons.add("추천 SSD는 M.2 규격이어야 합니다.");
        }

        if (!"NVME".equals(
                normalize(specs.get("interface")))) {
            reasons.add(
                    "추천 SSD는 NVMe 인터페이스여야 합니다.");
        }

        Double storage = positiveNumber(
                specs.get("storage_gb"));

        if (storage == null) {
            reasons.add(
                    "SSD 용량이 누락되었거나 유효하지 않습니다.");
        } else if (storage < rule.ssdMinGb()) {
            reasons.add("SSD 용량이 최소조건보다 작습니다.");
        }
    }

    private static void checkGpu(
            RecommendationRule rule,
            Map<String, String> specs,
            List<String> reasons) {

        if (!rule.requiresDiscreteGpu()) {
            return;
        }

        int actual = gpuLevel(
                normalize(specs.get("chipset")));

        int required = GPU_LEVELS.get(rule.gpuMinTier());

        if (actual == 0) {
            reasons.add(
                    "GPU 모델이 누락되었거나 등급표에 없습니다.");
        } else if (actual < required) {
            reasons.add("GPU 등급이 최소조건보다 낮습니다.");
        }

        if (rule.minVramGb() > 0) {
            Double vram = positiveNumber(
                    specs.get("vram_gb"));

            if (vram == null) {
                reasons.add(
                        "GPU VRAM이 누락되었거나 유효하지 않습니다.");
            } else if (vram < rule.minVramGb()) {
                reasons.add(
                        "GPU VRAM이 최소조건보다 작습니다.");
            }
        }
    }

    private static int gpuLevel(String model) {
        return switch (model) {
            case "GTX 1660 SUPER", "RTX 2060",
                 "RTX 2060 SUPER", "RTX 3050" -> 1;

            case "RTX 3060", "RTX 3060 TI",
                 "RTX 3070", "RTX 3070 TI",
                 "RTX 4060", "RTX 4060 TI",
                 "RTX 5050", "RTX 5060", "RTX 5060 TI",
                 "RX 7600", "RX 6800",
                 "RX 9060", "RX 9060 XT" -> 2;

            case "RTX 3080", "RTX 4070 SUPER",
                 "RTX 4070 TI SUPER",
                 "RTX 5070", "RTX 5070 TI",
                 "RX 9070", "RX 9070 GRE",
                 "RX 9070 XT" -> 3;

            case "RTX 4080 SUPER",
                 "RTX 5080", "RTX 5090" -> 4;

            default -> 0;
        };
    }

    private static String normalize(String value) {
        if (value == null) {
            return "";
        }

        return value.replaceAll("(?U)\\s+", " ")
                .trim()
                .toUpperCase(Locale.ROOT);
    }

    private static Double positiveNumber(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }

        try {
            double number = Double.parseDouble(value.trim());

            return Double.isFinite(number) && number > 0
                    ? number : null;
        } catch (NumberFormatException exception) {
            return null;
        }
    }
}
