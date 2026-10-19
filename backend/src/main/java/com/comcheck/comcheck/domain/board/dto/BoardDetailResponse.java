package com.comcheck.comcheck.domain.board.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.board.entity.Board;
import com.comcheck.comcheck.domain.board.entity.Category;

import lombok.Getter;

@Getter
public class BoardDetailResponse {
    private final Long boardId;
    private final Category category;
    private final String categoryLabel;
    private final String title;
    private final String content;
    private final Long writerId; // 작성자 회원 번호
    private final String writerName; // 작성자 이름
    private final long viewCount;
    private final boolean isDeleted;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    //게시판별 용도
    //공지
    private final boolean isPinned;
    //Q&A
    private final boolean isResolved;

    public BoardDetailResponse(Board board) {
        this.boardId = board.getBoardId();
        this.category = board.getCategory();
        this.categoryLabel = board.getCategory().getLabel();
        this.title = board.getTitle();
        this.content = board.getContent();
        this.writerId = board.getWriter().getUserId();
        this.writerName = board.getWriter().getNickname();
        this.viewCount = board.getViewCount();
        this.isDeleted = board.isDeleted();
        this.createdAt = board.getCreatedAt();
        this.updatedAt = board.getUpdatedAt();

        //게시판별 용도
        this.isPinned = board.isPinned();
        this.isResolved = board.isResolved();
    }
}
