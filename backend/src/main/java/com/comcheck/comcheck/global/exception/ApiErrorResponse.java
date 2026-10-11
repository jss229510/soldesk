package com.comcheck.comcheck.global.exception;

import java.time.LocalDateTime;
import java.util.Map;

// 예외 발생 시 모든 API가 같은 JSON 형태로 반환할 오류 응답 DTO다.
// record는 필드값을 담는 용도라 생성자·getter를 따로 작성하지 않아도 된다.
public record ApiErrorResponse(
        int status,                 // HTTP 상태 코드: 400, 401, 404 등
        String code,                // 상태를 구분하는 문자열 코드: NOT_FOUND 등
        String message,             // 사용자 또는 프론트에 전달할 오류 설명
        LocalDateTime timestamp,    // 오류 응답이 생성된 시각
        Map<String, String> errors  // 입력값 검증 오류처럼 필드별 메시지가 필요할 때 사용하는 공간
) {

}
