package com.comcheck.comcheck.domain.estimate.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

// 예산별 추천 조회에서 예산 값이 없거나 0 미만일 때 던지는 400 전용 예외
// ResponseStatusException을 상속하므로 GlobalExceptionHandler가 공통 JSON으로 바꿔준다.
public class InvalidBudgetException extends ResponseStatusException {

    public InvalidBudgetException(Long budget) {
        super(HttpStatus.BAD_REQUEST,
                budget == null
                        ? "예산(budget)을 입력하세요."
                        : "예산은 0원 이상이어야 합니다. 입력값: " + budget);
    }
}
