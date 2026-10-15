package com.comcheck.comcheck.domain.board.repository;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.board.entity.Board;
import com.comcheck.comcheck.domain.board.entity.Category;

public interface BoardRepository extends JpaRepository<Board, Long>{
    @EntityGraph(attributePaths = "writer")
    @Query(value = """
            SELECT b FROM Board b
             WHERE (:category IS NULL OR b.category= :category)
               AND (:keyword IS NULL
                    OR b.title LIKE CONCAT('%', :keyword, '%')
                    OR b.content LIKE CONCAT('%', :keyword, '%'))
            """, countQuery = """
            SELECT COUNT(b) FROM Board b
             WHERE (:category IS NULL OR b.category = :category)
               AND (:keyword IS NULL
                    OR b.title   LIKE CONCAT('%', :keyword, '%')
                    OR b.content LIKE CONCAT('%', :keyword, '%'))
                    """)
    Page<Board> search(@Param("category") Category category,
            @Param("keyword") String keyword,
            Pageable pageable);
}
