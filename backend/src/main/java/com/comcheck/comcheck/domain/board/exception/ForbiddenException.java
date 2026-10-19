package com.comcheck.comcheck.domain.board.exception;

public class ForbiddenException extends RuntimeException{
    // 403: 권한 불충분
    public ForbiddenException(String message){
        super(message);
    }
}
