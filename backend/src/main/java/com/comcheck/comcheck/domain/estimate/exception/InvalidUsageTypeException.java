package com.comcheck.comcheck.domain.estimate.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;

// 허용되지 않은 사용 용도(usageType) 값이 들어왔을 때 던지는 400 전용 예외
// 이 검사를 하지 않으면 DB의 CK_ESTIMATE_USAGE 제약조건에 걸려 500 오류가 나므로, 저장 전에 미리 막는다.
public class InvalidUsageTypeException extends ResponseStatusException {

    public InvalidUsageTypeException(String usageType) {
        // 허용 값 목록을 메시지에 함께 넣어 프론트가 무엇을 보내야 하는지 바로 알 수 있게 한다.
        super(HttpStatus.BAD_REQUEST,
                "사용 용도 '" + usageType + "'는 올바르지 않습니다. 허용 값: "
                        + Estimate.USAGE_TYPES);
    }
}
