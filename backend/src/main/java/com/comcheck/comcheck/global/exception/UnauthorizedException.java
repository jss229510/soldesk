package com.comcheck.comcheck.global.exception;

// 로그인하지 않은 사용자가 로그인이 필요한 기능에 접근했을 때 발생시키는 예외 클래스
public class UnauthorizedException extends RuntimeException{
    public UnauthorizedException(String message){
        super(message);
    }
}
