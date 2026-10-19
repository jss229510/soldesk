package com.comcheck.comcheck.domain.estimate.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

// 다른 회원의 견적을 보거나 수정·삭제하려고 할 때 던지는 403 전용 예외
// 401(로그인 안 함)과 다르다: 로그인은 했지만 "이 견적의 주인이 아니라서" 권한이 없는 경우다.
public class EstimateAccessDeniedException extends ResponseStatusException {

    public EstimateAccessDeniedException(Long estimateId) {
        super(HttpStatus.FORBIDDEN, "ID가 " + estimateId + "인 견적에 접근할 권한이 없습니다.");
    }
}
