package com.comcheck.comcheck.domain.board.entity;

public enum Category {
    FREE("자유게시판"),
    QNA("Q&A"),
    NOTICE("공지사항");

    private final String label;

    Category(String label){
        this.label = label;
    }

    public String getLabel(){
        return label;
    }

}
