package com.comcheck.comcheck.domain.build;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.comcheck.comcheck.domain.build.dto.ReplacementRequest;
import com.comcheck.comcheck.domain.build.dto.ReplacementCandidateResponse;
import com.comcheck.comcheck.domain.part.dto.PartResponse;
import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;
import com.comcheck.comcheck.domain.partspec.entity.PartSpec;
import com.comcheck.comcheck.domain.partspec.repository.PartSpecRepository;

@Service
@Transactional(readOnly = true)
public class ReplacementCandidateService {

    private static final Set<String> REQUIRED_CATEGORIES =
            Set.of("CPU", "MAINBOARD", "RAM", "SSD", "PSU");

    private static final Set<String> REPLACEABLE_CATEGORIES =
            Set.of("CPU", "MAINBOARD", "RAM", "SSD", "PSU", "GPU",
                    "CASE", "COOLER");

    private static final Set<String> UNCHECKED_ACCESSORY_CATEGORIES =
            Set.of("CASE", "COOLER");

    private final PartRepository partRepository;
    private final PartSpecRepository partSpecRepository;
    private final AccessoryRecommendationService accessoryService;

    public ReplacementCandidateService(
            PartRepository partRepository,
            PartSpecRepository partSpecRepository,
            AccessoryRecommendationService accessoryService) {

        this.partRepository = partRepository;
        this.partSpecRepository = partSpecRepository;
        this.accessoryService = accessoryService;
    }

    public record CurrentConfiguration(
            Map<String, Part> parts,
            Map<String, Long> quantities,
            Map<Long, Map<String, String>> specs) {
    }

    public List<ReplacementCandidateResponse> getCandidates(
            ReplacementRequest request) {

        CurrentConfiguration current = loadCurrentConfiguration(request);
        String category = normalize(request.category());
        Part selected = current.parts().get(category);

        if (selected.getPrice() == null || selected.getPrice() <= 0) {
            throw new IllegalArgumentException(
                    "현재 제품 가격을 확인할 수 없습니다.");
        }

        if (UNCHECKED_ACCESSORY_CATEGORIES.contains(category)) {
            return accessoryService.findRepresentatives(category).stream()
                    .filter(part -> !part.getPartId()
                            .equals(selected.getPartId()))
                    .limit(3)
                    .map(part -> new Candidate(part, Map.of()))
                    .map(candidate -> toResponse(candidate, selected))
                    .toList();
        }

        return findSameLevelCandidates(request, current).stream()
                .filter(candidate -> isCompatible(
                        request, current, category, candidate))
                .sorted(Comparator
                        .comparing((Candidate candidate) ->
                                candidate.part().getPrice())
                        .thenComparing(candidate ->
                                candidate.part().getPartId()))
                .limit(6)
                .map(candidate -> toResponse(candidate, selected))
                .toList();
    }

    public CurrentConfiguration loadCurrentConfiguration(
            ReplacementRequest request) {

        if (request == null) {
            throw new IllegalArgumentException(
                    "교체 요청이 필요합니다.");
        }

        RecommendationRule rule = RecommendationRule.find(
                request.usageType(),
                request.tierCode());

        String category = normalize(request.category());

        if (!REPLACEABLE_CATEGORIES.contains(category)) {
            throw new IllegalArgumentException(
                    "지원하지 않는 교체 부품 종류입니다.");
        }

        List<ReplacementRequest.SelectedPart> items =
                request.items();

        if (items == null || items.isEmpty()
                || items.size() > 8) {
            throw new IllegalArgumentException(
                    "현재 구성은 1개 이상 8개 이하여야 합니다.");
        }

        Map<Long, Long> quantitiesById = new HashMap<>();

        for (ReplacementRequest.SelectedPart item : items) {
            if (item == null
                    || item.partId() == null
                    || item.partId() < 1
                    || item.quantity() == null
                    || item.quantity() < 1) {
                throw new IllegalArgumentException(
                        "제품 번호와 수량은 양수여야 합니다.");
            }

            if (quantitiesById.putIfAbsent(
                    item.partId(), item.quantity()) != null) {
                throw new IllegalArgumentException(
                        "같은 제품이 중복되었습니다: "
                                + item.partId());
            }
        }

        List<Long> partIds =
                List.copyOf(quantitiesById.keySet());

        Map<Long, Part> partsById = partRepository
                .findAllById(partIds)
                .stream()
                .collect(Collectors.toMap(
                        Part::getPartId,
                        Function.identity()));

        Map<String, Part> parts = new HashMap<>();
        Map<String, Long> quantities = new HashMap<>();

        for (Long partId : partIds) {
            Part part = partsById.get(partId);

            if (part == null) {
                throw new IllegalArgumentException(
                        "존재하지 않는 제품입니다: " + partId);
            }

            String partCategory = normalize(part.getCategory());

            if (partCategory.isEmpty()) {
                throw new IllegalStateException(
                        "제품 카테고리가 없습니다: " + partId);
            }

            if (parts.putIfAbsent(partCategory, part) != null) {
                throw new IllegalArgumentException(
                        "같은 종류의 부품이 중복되었습니다: "
                                + partCategory);
            }

            quantities.put(
                    partCategory,
                    quantitiesById.get(partId));

            if (Set.of("CPU", "MAINBOARD", "GPU", "PSU")
                    .contains(partCategory)
                    && quantitiesById.get(partId) != 1L) {
                throw new IllegalArgumentException(
                        "CPU·메인보드·GPU·PSU는 각각 1개만 지원합니다.");
            }

            if (UNCHECKED_ACCESSORY_CATEGORIES.contains(partCategory)
                    && quantitiesById.get(partId) != 1L) {
                throw new IllegalArgumentException(
                        "케이스·쿨러는 각각 1개만 지원합니다.");
            }
        }

        if (!parts.keySet().containsAll(REQUIRED_CATEGORIES)) {
            throw new IllegalArgumentException(
                    "CPU·메인보드·RAM·SSD·PSU가 필요합니다.");
        }

        if (rule.requiresDiscreteGpu()
                && !parts.containsKey("GPU")) {
            throw new IllegalArgumentException(
                    "선택한 추천 용도에는 GPU가 필요합니다.");
        }

        if (!parts.containsKey(category)) {
            throw new IllegalArgumentException(
                    "현재 구성에 교체할 부품이 없습니다: "
                            + category);
        }

        return new CurrentConfiguration(
                Map.copyOf(parts),
                Map.copyOf(quantities),
                loadSpecs(List.copyOf(partsById.values())));
    }

    private record Candidate(
            Part part,
            Map<String, String> specs) {
    }

    private boolean isCompatible(
            ReplacementRequest request,
            CurrentConfiguration current,
            String category,
            Candidate candidate) {

        Map<String, Map<String, String>> configuration = new HashMap<>();

        for (Map.Entry<String, Part> entry : current.parts().entrySet()) {
            configuration.put(entry.getKey(),
                    current.specs().get(entry.getValue().getPartId()));
        }

        configuration.put(category, candidate.specs());

        for (String partCategory : List.of("CPU", "RAM", "SSD", "GPU")) {
            Map<String, String> specs = configuration.get(partCategory);

            if (specs != null && !MinimumRequirementChecker.check(
                    request.usageType(), request.tierCode(),
                    partCategory, specs,
                    current.quantities().get(partCategory)).passed()) {
                return false;
            }
        }

        if (!PlatformCompatibilityChecker.check(
                configuration.get("CPU"),
                configuration.get("MAINBOARD"),
                configuration.get("RAM"),
                current.quantities().get("RAM")).passed()) {
            return false;
        }

        if (!storageCompatible(
                configuration.get("MAINBOARD"),
                configuration.get("SSD"),
                current.quantities().get("SSD"))) {
            return false;
        }

        Map<String, String> gpu = configuration.get("GPU");

        if (gpu == null && !"Y".equals(normalize(
                configuration.get("CPU").get("has_igpu")))) {
            return false;
        }

        Double requiredWattage = gpu == null
                ? 400.0
                : positiveNumber(gpu.get("recommended_psu_watt"));

        Map<String, String> psu = configuration.get("PSU");
        Double wattage = positiveNumber(psu.get("wattage"));

        if (requiredWattage == null || wattage == null
                || wattage < requiredWattage) {
            return false;
        }

        if ("PSU".equals(category)) {
            Part selected = current.parts().get("PSU");
            String previousForm = normalize(current.specs()
                    .get(selected.getPartId()).get("form_factor"));
            String candidateForm = normalize(psu.get("form_factor"));

            if (previousForm.isEmpty()
                    || !previousForm.equals(candidateForm)) {
                return false;
            }
        }

        return true;
    }

    private boolean storageCompatible(
            Map<String, String> mainboard,
            Map<String, String> ssd,
            Long quantity) {

        if (!"M.2".equals(normalize(ssd.get("form_factor")))
                || !"NVME".equals(normalize(ssd.get("interface")))
                || !"Y".equals(normalize(mainboard.get("nvme_supported")))) {
            return false;
        }

        Double slots = positiveNumber(mainboard.get("m2_slots"));

        return slots != null && slots == Math.floor(slots)
                && quantity != null && quantity > 0
                && slots >= quantity;
    }

    private ReplacementCandidateResponse toResponse(
            Candidate candidate,
            Part selected) {

        Part part = candidate.part();
        PartResponse response = new PartResponse(
                part.getPartId(), part.getCategory(),
                part.getBrand(), part.getPartName(), part.getPrice(),
                part.getImageUrl(), part.getProductUrl(), false);

        return new ReplacementCandidateResponse(
                response,
                part.getPrice() - selected.getPrice(),
                candidate.specs(),
                UNCHECKED_ACCESSORY_CATEGORIES.contains(
                        normalize(part.getCategory()))
                        ? "대표 제품 목록입니다. 케이스·쿨러 호환성은 검사하지 않았습니다."
                        : "최소조건·교체 수준 조건·기본 호환성을 통과한 후보입니다.");
    }

    private List<Candidate> findSameLevelCandidates(
            ReplacementRequest request,
            CurrentConfiguration current) {

        String category = normalize(request.category());

        Part selected = current.parts().get(category);

        Map<String, String> selectedSpecs =
                current.specs().get(selected.getPartId());

        List<Part> products = partRepository
                .findByCategory(category)
                .stream()
                .filter(part -> !part.getPartId()
                        .equals(selected.getPartId()))
                .filter(part -> "N".equals(
                        normalize(part.getIsDiscontinued())))
                .filter(part -> part.getPrice() != null
                        && part.getPrice() > 0)
                .toList();

        Map<Long, Map<String, String>> candidateSpecs =
                loadSpecs(products);

        List<Candidate> candidates = new ArrayList<>();

        for (Part part : products) {
            Map<String, String> specs =
                    candidateSpecs.get(part.getPartId());

            boolean sameLevel =
                    MinimumRequirementChecker
                            .matchesReplacementLevel(
                                    category,
                                    selectedSpecs,
                                    specs);

            if (!sameLevel) {
                continue;
            }

            candidates.add(new Candidate(part, specs));
        }

        return List.copyOf(candidates);
    }

    private Map<Long, Map<String, String>> loadSpecs(
            List<Part> products) {

        if (products.isEmpty()) {
            return Map.of();
        }

        Map<Long, Map<String, String>> specs = new HashMap<>();

        for (Part part : products) {
            specs.put(part.getPartId(), new HashMap<>());
        }

        // Accessories are displayed without compatibility or performance checks.
        List<Long> partIds = products.stream()
                .filter(part -> !UNCHECKED_ACCESSORY_CATEGORIES.contains(
                        normalize(part.getCategory())))
                .map(Part::getPartId)
                .toList();

        List<PartSpec> rows = new ArrayList<>();

        for (int start = 0; start < partIds.size(); start += 500) {
            int end = Math.min(start + 500, partIds.size());
            rows.addAll(partSpecRepository
                    .findByPartIdInOrderByPartIdAscSpecIdAsc(
                            partIds.subList(start, end)));
        }

        for (PartSpec row : rows) {
            String key = row.getSpecKey();
            String value = row.getSpecValue();

            if (key == null || key.isBlank()
                    || value == null || value.isBlank()) {
                continue;
            }

            Map<String, String> partSpecs =
                    specs.get(row.getPartId());

            if (partSpecs == null) {
                throw new IllegalStateException(
                        "조회 범위 밖의 제품 스펙입니다.");
            }

            if (partSpecs.putIfAbsent(
                    key.trim(), value.trim()) != null) {
                throw new IllegalStateException(
                        "제품 스펙 항목이 중복되었습니다: "
                                + row.getPartId() + "/" + key);
            }
        }

        return specs.entrySet().stream()
                .collect(Collectors.toUnmodifiableMap(
                        Map.Entry::getKey,
                        entry -> Map.copyOf(entry.getValue())));
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

    private static String normalize(String value) {
        return value == null
                ? ""
                : value.trim().toUpperCase(Locale.ROOT);
    }
}
