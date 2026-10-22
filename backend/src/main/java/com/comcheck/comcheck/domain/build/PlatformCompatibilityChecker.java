package com.comcheck.comcheck.domain.build;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

public final class PlatformCompatibilityChecker {

    private static final Set<String> RAM_TYPES =
            Set.of("DDR3", "DDR4", "DDR5");

    private static final Pattern DDR_PATTERN =
            Pattern.compile("\\bDDR[345]\\b");

    private PlatformCompatibilityChecker() {
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
            Map<String, String> cpu,
            Map<String, String> mainboard,
            Map<String, String> ram,
            Long ramQuantity) {

        List<String> reasons = new ArrayList<>();

        if (cpu == null || mainboard == null || ram == null) {
            reasons.add("호환성 검사에 필요한 스펙이 없습니다.");
            return new Result(reasons);
        }

        String cpuSocket = normalize(cpu.get("cpu_socket"));
        String boardSocket =
                normalize(mainboard.get("cpu_socket"));

        if (cpuSocket.isEmpty() || boardSocket.isEmpty()) {
            reasons.add("CPU 소켓 정보를 확인할 수 없습니다.");
        } else if (!cpuSocket.equals(boardSocket)) {
            reasons.add("CPU와 메인보드 소켓이 다릅니다.");
        }

        String cpuDdr = normalize(cpu.get("DDR"));
        String boardDdr =
                normalize(mainboard.get("ram_type"));
        String ramDdr = normalize(ram.get("ram_type"));

        Set<String> supportedDdr = DDR_PATTERN
                .matcher(cpuDdr)
                .results()
                .map(match -> match.group())
                .collect(java.util.stream.Collectors.toSet());

        if (supportedDdr.isEmpty()) {
            reasons.add("CPU 지원 메모리 규격이 불명확합니다.");
        }

        if (!RAM_TYPES.contains(boardDdr)
                || !RAM_TYPES.contains(ramDdr)) {
            reasons.add("메인보드 또는 RAM 규격이 불명확합니다.");
        } else {
            if (!boardDdr.equals(ramDdr)) {
                reasons.add("메인보드와 RAM 규격이 다릅니다.");
            }

            if (!supportedDdr.isEmpty()
                    && !supportedDdr.contains(ramDdr)) {
                reasons.add("CPU가 해당 RAM 규격을 지원하지 않습니다.");
            }
        }

        Double slots = positiveNumber(
                mainboard.get("ram_socket"));
        Double modules = positiveNumber(
                ram.get("module_count"));
        Double capacity = positiveNumber(
                ram.get("capacity_gb"));
        Double maxCapacity = positiveNumber(
                mainboard.get("max_ram_capacity_gb"));

        boolean validSlots =
                slots != null && slots == Math.floor(slots);
        boolean validModules =
                modules != null && modules == Math.floor(modules);

        if (!validSlots || !validModules) {
            reasons.add("RAM 슬롯 수 또는 모듈 수가 불명확합니다.");
        }

        if (capacity == null || maxCapacity == null) {
            reasons.add("RAM 용량 또는 최대 지원 용량이 불명확합니다.");
        }

        if (ramQuantity == null || ramQuantity < 1) {
            reasons.add("RAM 구매 수량은 양의 정수여야 합니다.");
            return new Result(reasons);
        }

        if (validSlots && validModules
                && modules * ramQuantity > slots) {
            reasons.add("메인보드 RAM 슬롯 수가 부족합니다.");
        }

        if (capacity != null && maxCapacity != null
                && capacity * ramQuantity > maxCapacity) {
            reasons.add("메인보드의 최대 RAM 용량을 초과합니다.");
        }

        return new Result(reasons);
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