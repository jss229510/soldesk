package com.comcheck.comcheck.domain.partspec.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

// 요청한 부품에 속한 스펙을 찾지 못했을 때 사용하는 404 전용 예외다.
// ResponseStatusException을 상속하므로 GlobalExceptionHandler가 ApiErrorResponse로 변환한다.
public class PartSpecNotFoundException extends ResponseStatusException {

    public PartSpecNotFoundException(Long partId, Long specId) {
        super(
                HttpStatus.NOT_FOUND,
                "부품 ID가 " + partId + "인 스펙 ID " + specId + "를 찾을 수 없습니다.");
    }
}