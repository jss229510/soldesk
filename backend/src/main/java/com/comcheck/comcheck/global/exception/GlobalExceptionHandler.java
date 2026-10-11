package com.comcheck.comcheck.global.exception;

import java.time.LocalDateTime;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

// 여러 Controller와 Service에서 발생한 예외를 한곳에서 JSON 응답으로 바꾸는 전역 처리기다.
@RestControllerAdvice
public class GlobalExceptionHandler {

    // UserService 등이 던지는 ResponseStatusException을 가로채 공통 오류 응답으로 변환한다.
    // @ExceptionHandler(예외타입.class)는 "이 예외 또는 그 자식 예외가 발생하면 아래 메서드를 실행"하라는 Spring 표시다.
    // 따라서 ResponseStatusException을 상속한 PartNotFoundException도 이 메서드가 자동으로 처리한다.
    @ExceptionHandler(ResponseStatusException.class)
    // ResponseEntity는 HTTP 상태 코드와 JSON 본문을 함께 담는 응답 상자다.
    // <ApiErrorResponse>는 그 상자 안에 들어갈 JSON 데이터의 타입을 뜻한다.
    // handleResponseStatusException은 메서드 이름이므로 이해하기 쉬운 다른 이름으로 바꿔도 된다.
    public ResponseEntity<ApiErrorResponse> handleResponseStatusException(
            // Spring이 실제로 발생한 예외 객체를 이 변수에 자동으로 넣어준다.
            // 그래서 아래에서 exception.getReason()으로 Service가 지정한 오류 문구를 꺼낼 수 있다.
            ResponseStatusException exception) {

        // 예외에 담긴 HTTP 상태값(예: 404)을 HttpStatus enum으로 변환한다.
        HttpStatus status = HttpStatus.valueOf(exception.getStatusCode().value());

        // 프론트가 어떤 API 오류를 받아도 같은 필드명으로 처리할 수 있게 응답 형식을 고정한다.
        ApiErrorResponse response = new ApiErrorResponse(
                status.value(),             // 실제 HTTP 상태 코드: 400, 401, 404 등
                status.name(),              // 기본 오류 코드: BAD_REQUEST, NOT_FOUND 등
                exception.getReason(),      // Service에서 지정한 사용자용 오류 문구
                LocalDateTime.now(),        // 오류 응답을 만든 시각
                Map.of());                  // 현재는 필드별 오류가 없어 빈 Map으로 반환

        // HTTP 상태 코드와 JSON 본문을 함께 클라이언트에 전송한다.
        return ResponseEntity.status(status).body(response);
    }
}
