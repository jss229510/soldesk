package com.comcheck.comcheck.domain.estimate.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.estimate.dto.EstimatePartSpecRow;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;

import java.util.List;
import java.util.Optional;

public interface EstimateRepository extends JpaRepository<Estimate, Long> {

  // 특정 회원의 견적 목록(최신순)
  List<Estimate> findByUser_UserIdOrderByCreatedAtDesc(Long userId);

  // 추천 견적 목록
  // 회원이 없는 공용 견적도 목록에 남도록 LEFT JOIN으로 조회한다.
  @Query(value = """
      select e from Estimate e left join fetch e.user
      where e.isRecommend = :recommend
        and (:usageType is null or e.usageType = :usageType)
        and (:tierCode is null or e.tierCode = :tierCode)
      order by e.totalPrice asc
      """, countQuery = """
      select count(e) from Estimate e
      where e.isRecommend = :recommend
        and (:usageType is null or e.usageType = :usageType)
        and (:tierCode is null or e.tierCode = :tierCode)
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
  // 예산 이하에서 가장 비싼 견적을 먼저 조회한다. 동액이면 견적 번호순이다.
  @Query("""
      select e from Estimate e left join fetch e.user
      where e.isRecommend = :recommend
      and e.totalPrice <= :budget
      order by e.totalPrice desc, e.estimatedId asc
      """)

  // 서비스에서 최대 1건으로 제한하며 전체 개수는 조회하지 않는다.
  List<Estimate> findRecommendedWithinBudget(
      @Param("recommend") Boolean recommend,
      @Param("budget") Long budget,
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

  // 스펙이 없는 부품도 남겨, GPU/PSU가 없는 경우와 정보가 없는 경우를 구분한다.
  @Query("""
      select new com.comcheck.comcheck.domain.estimate.dto.EstimatePartSpecRow(
          p.partId, p.category, ps.specKey, ps.specValue, 1L)
      from Part p
      left join PartSpec ps on ps.partId = p.partId and ps.specKey in :specKeys
      where p.partId in :partIds
      """)
  List<EstimatePartSpecRow> findPowerSpecsByPartIds(
      @Param("partIds") List<Long> partIds,
      @Param("specKeys") List<String> specKeys);
}
