package com.comcheck.comcheck.domain.board.dto;

import java.util.List;

import org.springframework.data.domain.Page;

import com.comcheck.comcheck.domain.board.entity.Board;

import lombok.Getter;

@Getter 
public class BoardPageResponse {
    private final List<BoardListResponse> boards;
    private final int page;
    private final int size;
    private final long totalElements;
    private final int totalPages;
    private final boolean first;
    private final boolean last;

    public BoardPageResponse(List<BoardListResponse> boards, Page<Board> result){
        this.boards = boards;
        this.page = result.getNumber();
        this.size = result.getSize();
        this.totalElements = result.getTotalElements();
        this.totalPages = result.getTotalPages();
        this.first = result.isFirst();
        this.last = result.isLast();
    }
}
