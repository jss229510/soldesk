package com.comcheck.comcheck.domain.board.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.board.entity.Board;
import com.comcheck.comcheck.domain.board.entity.Category;

import lombok.Getter;

@Getter
public class BoardListResponse {
    //공통
    private final Long boardId;
    private final Category category;
    private final String categoryLabel;
    private final String title;
    private final String writerName; // User에서 Nikename만 가져오기
    private final long viewCount;
    private final boolean isDeleted;
    private final LocalDateTime createdAt;

    //게시판별 용도
    //공지
    private final boolean isPinned;
    //Q&A
    private final boolean isResolved;

    public BoardListResponse(Board board) {
        this.boardId = board.getBoardId();
        this.category = board.getCategory();
        this.categoryLabel = board.getCategory().getLabel();
        this.title = board.getTitle();
        this.writerName = board.getWriter().getNickname(); // 글 → 작성자 → 이름 (Service 트랜잭션 안에서 호출됨)
        this.viewCount = board.getViewCount();
        this.isDeleted = board.isDeleted();
        this.createdAt = board.getCreatedAt();

        //게시판별 용도
        this.isPinned = board.isPinned();
        this.isResolved = board.isResolved();
    }
}
