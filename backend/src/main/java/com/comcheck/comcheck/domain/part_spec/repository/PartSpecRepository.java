package com.comcheck.comcheck.domain.part_spec.repository;

import com.comcheck.comcheck.domain.part_spec.entity.part_spec;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PartSpecRepository extends JpaRepository<part_spec, Long> {
    
    // JpaRepository를 상속받아 PART_SPECS 테이블의 기본적인
    // 조회, 저장, 수정, 삭제 기능을 사용할 수 있음
}
