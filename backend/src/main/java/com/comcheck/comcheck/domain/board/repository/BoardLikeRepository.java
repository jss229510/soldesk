package com.comcheck.comcheck.domain.board.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.board.entity.BoardLike;

public interface BoardLikeRepository extends JpaRepository<BoardLike, BoardLike.BoardLikeId> {

    boolean existsByBoardBoardIdAndUserUserId(Long boardId, Long userId);

    long countByBoardBoardId(Long boardId);

    long deleteByBoardBoardIdAndUserUserId(Long boardId, Long userId);
}
