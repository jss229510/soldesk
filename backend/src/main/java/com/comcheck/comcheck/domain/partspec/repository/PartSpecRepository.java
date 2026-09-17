package com.comcheck.comcheck.domain.partspec.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.partspec.entity.PartSpec;

public interface PartSpecRepository extends JpaRepository<PartSpec, Long> {
    
    // JpaRepository를 상속받아 PART_SPECS 테이블의 기본적인
    // 조회, 저장, 수정, 삭제 기능을 사용할 수 있음
}
