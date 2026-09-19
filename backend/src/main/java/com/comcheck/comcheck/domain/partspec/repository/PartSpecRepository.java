package com.comcheck.comcheck.domain.partspec.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.partspec.entity.PartSpec;

import java.util.List;
import java.util.Optional;

public interface PartSpecRepository extends JpaRepository<PartSpec, Long> {
    
    // JpaRepository를 상속받아 PART_SPECS 테이블의 기본적인
    // 조회, 저장, 수정, 삭제 기능을 사용할 수 있음


    // 특정 부품(partId)의 스펙 목록을 spec_id 순서대로 조회
    // 메서드 이름만으로 Spring Data JPA가 아래 쿼리를 만들어 줌
    List<PartSpec> findByPartIdOrderBySpecIdAsc(Long partId);

     // 스펙 하나를 조회하되, 해당 부품에 속한 스펙인지까지 함께 확인
    Optional<PartSpec> findBySpecIdAndPartId(Long specId, Long partId);


}
