package com.comcheck.comcheck.domain.estimate.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

// 존재하지 않는 견적 번호/키로 조회했을 때 던지는 404 전용 예외
// ResponseStatusException을 상속하므로 GlobalExceptionHandler의
// @ExceptionHandler(ResponseStatusException.class)가 자동으로 잡아서 공통 JSON(ApiErrorResponse)으로 바꾼다.
// → 전역 Handler를 고칠 필요가 없다. (PartNotFoundException과 같은 방식)
public class EstimateNotFoundException extends ResponseStatusException {

    // 견적 번호(PK)로 찾지 못했을 때
    public EstimateNotFoundException(Long estimateId) {
        super(HttpStatus.NOT_FOUND, "ID가 " + estimateId + "인 견적을 찾을 수 없습니다.");
    }

    // 외부 공개용 키로 찾지 못했을 때
    public EstimateNotFoundException(String estimateKey) {
        super(HttpStatus.NOT_FOUND, "키가 " + estimateKey + "인 견적을 찾을 수 없습니다.");
    }
}