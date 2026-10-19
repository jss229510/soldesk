package com.comcheck.comcheck.domain.estimate.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.estimate.dto.EstimatePartSpecRow;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;

import java.util.List;
import java.util.Optional;

public interface EstimateRepository extends JpaRepository<Estimate, Long> {

  // 특정 회원의 견적 목록(최신순)
  Estimate findByUser_UserIdOrderByCreatedAtDesc(Long userId);

  // 추천 견적 목록
  @EntityGraph(attributePaths = "user")
  @Query("""
      select e from Estimate e
      where e.isRecommend = :recommend
        and (:usageType is null or e.usageType = :usageType)
        and (:tierCode is null or e.tierCode = :tierCode)
      order by e.totalPrice asc
      """)
  Page<Estimate> findRecommended(
      @Param("recommend") Boolean recommend,
      @Param("usageType") String usageType,
      @Param("tierCode") String tierCode,
      Pageable pageable);

  // Estimate Key로 견적 하나 조회
  // 결과가 없을 수 있으므로 Optional로 감싸서 반환
  Optional<Estimate> findByEstimateKey(String estimateKey);

  // 예산별 추천
  // 추천 견적 + 총 금액이 예산 이하
  @EntityGraph(attributePaths = "user") // 목록의 각 견적마다 회원을 따로 조회하는 N+1 문제를 막기 위해 user를 함께 조인해서 가져온다
  @Query("""
      select e from Estimate e
      where e.isRecommend = :recommend
      and e.totalPrice <= :budget
      and (:usageType is null or e.usageType = :usageType)
      order by e.totalPrice desc
      """)

  // Page : 목록 + 전체 개수 + 전체 페이지 수 정보를 함께 담는다.
  Page<Estimate> findRecommendedWithinBudget(
      @Param("recommend") Boolean recommend,
      @Param("budget") Long budget,
      @Param("usageType") String usageType,
      Pageable pageable);

  // 전력 검사에 필요한 스펙만 골라서 조회
  @Query("""
      select new com.comcheck.comcheck.domain.estimate.dto.EstimatePartSpecRow(
          p.partId, p.category, ps.specKey, ps.specValue, ei.quantity)
      from EstimateItem ei
      join ei.part p
      join PartSpec ps on ps.partId = p.partId
      where ei.estimate.estimatedId = :estimateId
        and ps.specKey in :specKeys
      """)
  List<EstimatePartSpecRow> findPowerSpecs(
      @Param("estimateId") Long estimateId,
      @Param("specKeys") List<String> specKeys);
}
