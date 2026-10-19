package com.comcheck.comcheck.domain.Board.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.Board.entity.Board;
import com.comcheck.comcheck.domain.Board.entity.Category;

import lombok.Getter;

@Getter 
public class BoardDetailResponse {
    
    private final Long boardId;
    private final Category category;
    private final String categoryLabel;
    private final String title;
    private final String content;
    private final Long writerId;           // 작성자 회원 번호
    private final String writerName;       // 작성자 이름
    private final long viewCount;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    public BoardDetailResponse(Board board) {
        this.boardId = board.getBoardId();
        this.category = board.getCategory();
        this.categoryLabel = board.getCategory().getLabel();
        this.title = board.getTitle();
        this.content = board.getContent();
        this.writerId = board.getWriter().getMemberId();
        this.writerName = board.getWriter().getName();
        this.viewCount = board.getViewCount();
        this.createdAt = board.getCreatedAt();
        this.updatedAt = board.getUpdatedAt();
    }
}

