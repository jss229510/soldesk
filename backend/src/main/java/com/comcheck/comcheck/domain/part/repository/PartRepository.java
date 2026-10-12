package com.comcheck.comcheck.domain.part.repository;

import java.util.List;
import com.comcheck.comcheck.domain.part.entity.Part;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface PartRepository extends JpaRepository<Part, Long> {

    // @Query 안의 p는 Part Entity의 별칭이다. 실제 DB 테이블명(PARTS)이 아니라 Entity 필드명을 사용한다.
    // category가 null이면 카테고리 조건을 건너뛰고, 값이 있으면 정확히 일치하는 부품만 조회한다.
    // keyword가 null이면 검색 조건을 건너뛰고, 값이 있으면 제품명 또는 브랜드에 포함된 부품을 찾는다.
    @Query("""
            select p
            from Part p
            where (:category is null or p.category = :category)
            and (
            :keyword is null
            or lower(p.partName) like lower(concat('%', :keyword, '%'))
            or lower(p.brand) like lower(concat('%', :keyword, '%'))
            )
                """)

    // @Param 이름은 JPQL의 :category, :keyword 자리에 각각 어떤 값을 넣을지 연결한다.
    List<Part> searchByCategoryAndKeyword(
            @Param("category") String category,
            @Param("keyword") String keyword);

    // JpaRepository를 상속받아 PARTS 테이블의 기본적인
    // 조회, 저장, 수정, 삭제 기능을 사용할 수 있음
    List<Part> findByCategory(String category);
}
