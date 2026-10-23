package com.comcheck.comcheck.domain.build;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.estimateitem.repository.EstimateItemRepository;
import com.comcheck.comcheck.domain.part.entity.Part;

import jakarta.persistence.EntityManager;
import jakarta.persistence.LockModeType;

@Service
public class RecommendationAccessoryWriter {

    private static final Set<String> REQUIRED_CATEGORIES =
            Set.of("CPU", "MAINBOARD", "RAM", "SSD", "PSU");

    private final EstimateRepository estimateRepository;
    private final EstimateItemRepository itemRepository;
    private final AccessoryRecommendationService accessoryService;
    private final EntityManager entityManager;

    public RecommendationAccessoryWriter(
            EstimateRepository estimateRepository,
            EstimateItemRepository itemRepository,
            AccessoryRecommendationService accessoryService,
            EntityManager entityManager) {

        this.estimateRepository = estimateRepository;
        this.itemRepository = itemRepository;
        this.accessoryService = accessoryService;
        this.entityManager = entityManager;
    }

    @Transactional
    public int applyDefaults(String dateCode) {
        if (dateCode == null || !dateCode.matches("[0-9]{8}")) {
            throw new IllegalArgumentException(
                    "추천 날짜는 YYYYMMDD 형식이어야 합니다.");
        }

        String prefix = dateCode + "_";

        List<Estimate> estimates = estimateRepository
                .findRecommended(true, null, null, Pageable.unpaged())
                .getContent()
                .stream()
                .filter(estimate -> estimate.getUser() == null)
                .filter(estimate -> estimate.getEstimateKey() != null
                        && estimate.getEstimateKey().startsWith(prefix))
                .sorted(Comparator.comparing(Estimate::getEstimatedId))
                .toList();

        if (estimates.isEmpty()) {
            throw new IllegalArgumentException(
                    "해당 날짜의 공용 추천 견적이 없습니다.");
        }

        for (Estimate estimate : estimates) {
            entityManager.refresh(estimate, LockModeType.PESSIMISTIC_WRITE);

            if (!Boolean.TRUE.equals(estimate.getIsRecommend())
                    || estimate.getUser() != null) {
                throw new IllegalStateException(
                        "공용 추천 견적만 변경할 수 있습니다.");
            }

            applyToEstimate(estimate);
        }

        return estimates.size();
    }

    private void applyToEstimate(Estimate estimate) {
        List<EstimateItem> items = new ArrayList<>(
                itemRepository.findByEstimate_EstimatedId(
                        estimate.getEstimatedId()));

        Set<String> categories = items.stream()
                .map(item -> item.getPart().getCategory())
                .collect(Collectors.toSet());

        if (!categories.containsAll(REQUIRED_CATEGORIES)) {
            throw new IllegalStateException(
                    "필수 부품이 누락된 추천 견적입니다: "
                            + estimate.getEstimatedId());
        }

        Map<String, Part> defaults = accessoryService
                .selectDefaults(estimate.getUsageType());

        for (String category : List.of("CASE", "COOLER")) {
            replaceAccessory(estimate, items, category, defaults.get(category));
        }

        long totalPrice = 0;

        for (EstimateItem item : items) {
            totalPrice = Math.addExact(totalPrice, item.calculateItemPrice());
        }

        estimate.changeTotals(totalPrice, estimate.getTotalPower());
    }

    private void replaceAccessory(
            Estimate estimate,
            List<EstimateItem> items,
            String category,
            Part selected) {

        List<EstimateItem> previous = items.stream()
                .filter(item -> category.equals(item.getPart().getCategory()))
                .toList();

        if (previous.size() == 1) {
            EstimateItem current = previous.get(0);

            if (current.getPart().getPartId().equals(selected.getPartId())
                    && Long.valueOf(1).equals(current.getQuantity())) {
                return;
            }
        }

        if (!previous.isEmpty()) {
            itemRepository.deleteAll(previous);
            itemRepository.flush();
            items.removeAll(previous);
        }

        EstimateItem added = itemRepository.save(
                new EstimateItem(estimate, selected, 1L));

        items.add(added);
    }
}
