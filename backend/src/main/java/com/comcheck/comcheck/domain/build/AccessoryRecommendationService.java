package com.comcheck.comcheck.domain.build;

import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;

@Service
@Transactional(readOnly = true)
public class AccessoryRecommendationService {

    private static final String PRODUCT_URL =
            "https://prod.danawa.com/info/?pcode=";

    private static final Map<String, Set<String>> CATALOG =
            Map.of(
                    "CASE", Set.of(
                            PRODUCT_URL + "122694968&cate=112775",
                            PRODUCT_URL + "124076069&cate=112775",
                            PRODUCT_URL + "79559156&cate=112775",
                            PRODUCT_URL + "92045654&cate=112775"
                    ),
                    "COOLER", Set.of(
                            PRODUCT_URL + "106047347&cate=11336857",
                            PRODUCT_URL + "92108297&cate=11336857",
                            PRODUCT_URL + "64377734&cate=11336856",
                            PRODUCT_URL + "92045246&cate=11336856"
                    )
            );

    private final PartRepository partRepository;

    public AccessoryRecommendationService(
            PartRepository partRepository) {

        this.partRepository = partRepository;
    }

    public Map<String, Part> selectDefaults(String usageType) {
        int index = switch (normalize(usageType)) {
            case "OFFICE" -> 0;
            case "GAMING" -> 1;
            case "STREAMING" -> 2;
            case "CREATOR" -> 3;
            default -> throw new IllegalArgumentException(
                    "지원하지 않는 용도입니다: " + usageType);
        };

        List<Part> cases = findRepresentatives("CASE");
        List<Part> coolers = findRepresentatives("COOLER");

        if (cases.size() != 4 || coolers.size() != 4) {
            throw new IllegalStateException(
                    "판매 중인 대표 케이스·쿨러가 각각 4개 필요합니다.");
        }

        return Map.of(
                "CASE", cases.get(index),
                "COOLER", coolers.get(index));
    }

    public List<Part> findRepresentatives(String category) {
        String normalizedCategory = normalize(category);
        Set<String> urls = CATALOG.get(normalizedCategory);

        if (urls == null) {
            throw new IllegalArgumentException(
                    "지원하지 않는 대표 부품 종류입니다: "
                            + category);
        }

        List<Part> registered = partRepository
                .findByCategory(normalizedCategory)
                .stream()
                .filter(part -> urls.contains(part.getProductUrl()))
                .toList();

        long uniqueUrls = registered.stream()
                .map(Part::getProductUrl)
                .distinct()
                .count();

        if (uniqueUrls != registered.size()) {
            throw new IllegalStateException(
                    "대표 제품 URL이 DB에 중복 등록되어 있습니다.");
        }

        return registered.stream()
                .filter(part -> "N".equals(
                        normalize(part.getIsDiscontinued())))
                .filter(part -> part.getPrice() != null
                        && part.getPrice() > 0)
                .sorted(Comparator
                        .comparing(Part::getPrice)
                        .thenComparing(Part::getPartId))
                .toList();
    }

    private static String normalize(String value) {
        return value == null
                ? ""
                : value.trim().toUpperCase(Locale.ROOT);
    }
}
