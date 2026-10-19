package com.comcheck.comcheck.domain.Board.dto;

import java.time.LocalDateTime;

import com.comcheck.comcheck.domain.Board.entity.Board;
import com.comcheck.comcheck.domain.Board.entity.Category;

import lombok.Getter;

@Getter 
public class BoardListResponse {
    
    private final Long boardId;
    private final Category category;    //Json에서는 "CAFE"
    private final String categoryLabel; //한글이름 "카페"
    private final String title;
    private final String writerName;       // 작성자 이름 (Member 객체에서 이름만 꺼낸다)
    private final long viewCount;
    private final LocalDateTime createdAt;

    public BoardListResponse(Board board) {
        this.boardId = board.getBoardId();
        this.category = board.getCategory();
        this.categoryLabel = board.getCategory().getLabel();
        this.title = board.getTitle();
        this.writerName = board.getWriter().getName(); // 글 → 작성자 → 이름 (Service 트랜잭션 안에서 호출됨)
        this.viewCount = board.getViewCount();
        this.createdAt = board.getCreatedAt();
    }
}

