package com.comcheck.comcheck.domain.board.repository;

import java.util.List;

import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.board.entity.BoardComment;

public interface BoardCommentRepository extends JpaRepository<BoardComment, Long> {

    @EntityGraph(attributePaths = "writer")
    List<BoardComment> findByBoardBoardIdAndIsDeletedFalseOrderByCreatedAtAsc(Long boardId);
}
