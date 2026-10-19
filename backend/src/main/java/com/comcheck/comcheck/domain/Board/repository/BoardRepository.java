package com.comcheck.comcheck.domain.Board.repository;



import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.comcheck.comcheck.domain.Board.entity.Board;
import com.comcheck.comcheck.domain.Board.entity.Category;

public interface BoardRepository extends JpaRepository<Board, Long>{
    
    // chapter04 기준
    /*
    findAll(전부 찾아라) + By +OrderBy(정렬) + BoardId(글번호)+Desc
    select * from board order by board_id desc
    @EntityGraph(attributePaths = "writer"): 글 가져올 때 작성자도 Join으로 한번에 같이 가져오기
    */

    /*
    @EntityGraph(attributePaths = "writer")
    List<Board> findAllByOrderByBoardIdDesc(); 
    */

    @EntityGraph(attributePaths = "writer")
    @Query(value = """
            SELECT b FROM Board b
             WHERE (:category IS NULL OR b.category = :category)
               AND (:keyword IS NULL
                    OR b.title   LIKE CONCAT('%', :keyword, '%')
                    OR b.content LIKE CONCAT('%', :keyword, '%'))
            """,
           countQuery = """
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

