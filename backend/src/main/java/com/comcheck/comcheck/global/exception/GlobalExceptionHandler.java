package com.comcheck.comcheck.global.exception;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.server.ResponseStatusException;

// 여러 Controller와 Service에서 발생한 예외를 한곳에서 JSON 응답으로 바꾸는 전역 처리기다.
@RestControllerAdvice
public class GlobalExceptionHandler {

    // 예상하지 못한 서버 오류의 실제 원인은 응답에 노출하지 않고 서버 로그에만 남긴다.
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    // @Valid DTO의 필드 규칙을 어긴 경우에도 프로젝트 공통 오류 JSON을 반환한다.
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiErrorResponse> handleValidationException(MethodArgumentNotValidException exception) {
        Map<String, String> errors = new LinkedHashMap<>();

        for (FieldError fieldError : exception.getBindingResult().getFieldErrors()) {
            errors.putIfAbsent(fieldError.getField(), fieldError.getDefaultMessage());
        }

        ApiErrorResponse response = new ApiErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                HttpStatus.BAD_REQUEST.name(),
                "입력값을 다시 확인해주세요.",
                LocalDateTime.now(),
                errors
        );

        return ResponseEntity.badRequest().body(response);
    }

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

    // /api/payments/abc처럼 Long 자리에 문자가 들어온 경우 발생한다.
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<ApiErrorResponse> handleTypeMismatch(
            MethodArgumentTypeMismatchException exception) {
        Map<String, String> errors = Map.of(
                exception.getName(),
                "요청값의 형식이 올바르지 않습니다.");

        return errorResponse(
                HttpStatus.BAD_REQUEST,
                "URL 또는 요청 파라미터의 형식을 다시 확인해주세요.",
                errors);
    }

    // @RequestParam으로 선언한 pg_token 같은 필수 파라미터가 없는 경우 발생한다.
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<ApiErrorResponse> handleMissingRequestParameter(
            MissingServletRequestParameterException exception) {
        Map<String, String> errors = Map.of(
                exception.getParameterName(),
                "필수 요청값입니다.");

        return errorResponse(
                HttpStatus.BAD_REQUEST,
                "필수 요청값이 누락되었습니다.",
                errors);
    }

    // JSON 문법이 틀렸거나 필드 타입과 다른 값이 들어온 경우 발생한다.
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiErrorResponse> handleUnreadableMessage(
            HttpMessageNotReadableException exception) {
        return errorResponse(
                HttpStatus.BAD_REQUEST,
                "요청 본문의 JSON 형식이 올바르지 않습니다.");
    }

    // 생성자나 도메인 객체가 잘못된 값 자체를 거부한 경우 400으로 변환한다.
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ApiErrorResponse> handleIllegalArgument(
            IllegalArgumentException exception) {
        return errorResponse(
                HttpStatus.BAD_REQUEST,
                exception.getMessage());
    }

    // 결제 준비 상태가 아닌데 승인하는 경우처럼 현재 상태에서 허용되지 않는 요청을 처리한다.
    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<ApiErrorResponse> handleIllegalState(
            IllegalStateException exception) {
        return errorResponse(
                HttpStatus.CONFLICT,
                exception.getMessage());
    }

    // UNIQUE, NOT NULL, FK 같은 DB 제약조건 위반은 내부 SQL을 숨기고 공통 메시지만 반환한다.
    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<ApiErrorResponse> handleDataIntegrityViolation(
            DataIntegrityViolationException exception) {
        log.warn("데이터 무결성 제약조건 위반", exception);
        return errorResponse(
                HttpStatus.CONFLICT,
                "이미 처리된 데이터이거나 현재 상태에서 저장할 수 없습니다.");
    }

    // 410 삭제된 게시물입니다.
    @ExceptionHandler(DeletedBoardException.class)
    public ResponseEntity<ApiErrorResponse> handleDeletedBoard(DeletedBoardException e){
        return errorResponse(HttpStatus.GONE, e.getMessage()); // 410

    }

    // 401 로그인 필요한 작업입니다.
    @ExceptionHandler(UnauthorizedException.class)
    public ResponseEntity<ApiErrorResponse> handleUnauthorized(UnauthorizedException e){
        return errorResponse(HttpStatus.UNAUTHORIZED, e.getMessage());
    }

    // 403 수정·삭제 권한 없음
    @ExceptionHandler(ForbiddenException.class)
    public ResponseEntity<ApiErrorResponse> handleForbidden(ForbiddenException e){
        return errorResponse(HttpStatus.FORBIDDEN, e.getMessage());
    }

    // 404 게시물이 존재하지 않습니다
    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<ApiErrorResponse> handleNotFound(NotFoundException e){
        return errorResponse(HttpStatus.NOT_FOUND, e.getMessage());
    }

    private ResponseEntity<ApiErrorResponse> errorResponse(HttpStatus status, String message){
        return errorResponse(status, message, Map.of());
    }

    // 필드별 오류가 필요한 예외도 동일한 ApiErrorResponse 구조로 만들기 위한 공통 메서드다.
    private ResponseEntity<ApiErrorResponse> errorResponse(
            HttpStatus status,
            String message,
            Map<String, String> errors) {
        ApiErrorResponse response = new ApiErrorResponse(
            status.value(),
            status.name(),
            message,
            LocalDateTime.now(),
            errors
        );
        return ResponseEntity.status(status).body(response);
    }

    // 위에서 구체적으로 분류하지 못한 오류의 세부 내용은 사용자에게 노출하지 않는다.
    // 반드시 가장 아래에 두어 구체적인 예외 처리기가 먼저 선택되게 한다.
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiErrorResponse> handleUnexpectedException(Exception exception) {
        log.error("처리되지 않은 서버 예외", exception);
        return errorResponse(
                HttpStatus.INTERNAL_SERVER_ERROR,
                "서버 처리 중 오류가 발생했습니다.");
    }

}
