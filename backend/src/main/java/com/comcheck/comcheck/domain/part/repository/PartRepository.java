package com.comcheck.comcheck.domain.part.repository;

import java.util.List;
import com.comcheck.comcheck.domain.part.entity.Part;
import org.springframework.data.jpa.repository.JpaRepository;


public interface PartRepository extends JpaRepository<Part, Long> {

    // JpaRepository를 상속받아 PARTS 테이블의 기본적인
    // 조회, 저장, 수정, 삭제 기능을 사용할 수 있음
    List<Part> findByCategory(String category);
}