package com.comcheck.comcheck.domain.board.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.board.entity.BoardComment;

public record BoardCommentResponse(
        Long commentId,
        Long writerId,
        String writerName,
        String content,
        LocalDateTime createdAt,
        LocalDateTime updatedAt) {

    public BoardCommentResponse(BoardComment comment) {
        this(
                comment.getCommentId(),
                comment.getWriter().getUserId(),
                comment.getWriter().getNickname(),
                comment.getContent(),
                comment.getCreatedAt(),
                comment.getUpdatedAt());
    }
}
