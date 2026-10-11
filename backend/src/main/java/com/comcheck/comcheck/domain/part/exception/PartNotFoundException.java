package com.comcheck.comcheck.domain.part.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

// 존재하지 않는 부품 ID를 조회했을 때 Service가 던지는 404 전용 예외다.
// ResponseStatusException을 상속하므로 GlobalExceptionHandler가 공통 JSON 오류 응답으로 바꾼다.
public class PartNotFoundException extends ResponseStatusException {
    public PartNotFoundException(Long partId) {
        // 어떤 ID를 찾지 못했는지 프론트와 개발자가 바로 알 수 있도록 오류 문구에 포함한다.
        super(
            HttpStatus.NOT_FOUND,
            "ID가 " + partId + "인 부품을 찾을 수 없습니다."
        );
    }
}
