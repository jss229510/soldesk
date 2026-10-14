package com.comcheck.comcheck.global.exception;

import java.io.IOException;
import java.time.LocalDateTime;

import jakarta.servlet.http.HttpServletResponse;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

// Controller 밖의 Spring Security 오류도 ApiErrorResponse 형식으로 기록한다.
@Component
public class SecurityErrorResponseWriter {

    public void write(HttpServletResponse response, HttpStatus status, String message) throws IOException {
        response.setStatus(status.value());
        response.setContentType("application/json;charset=UTF-8");

        // Security 단계의 메시지는 서버가 고정해 전달하므로 JSON 이스케이프 대상인 사용자 입력값이 없다.
        String body = "{\"status\":" + status.value()
                + ",\"code\":\"" + status.name()
                + "\",\"message\":\"" + message
                + "\",\"timestamp\":\"" + LocalDateTime.now()
                + "\",\"errors\":{}}";
        response.getWriter().write(body);
    }
}
