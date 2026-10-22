package com.comcheck.comcheck.domain.estimate.dto;

import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import tools.jackson.core.JacksonException;
import tools.jackson.core.JsonParser;
import tools.jackson.core.JsonToken;
import tools.jackson.databind.DeserializationContext;
import tools.jackson.databind.ValueDeserializer;
import tools.jackson.databind.annotation.JsonDeserialize;

// 화면에서 교체한 구성은 저장하지 않고, 부품 ID로 DB 스펙을 조회해 검사한다.
public record EstimatePowerCheckRequest(
        @NotEmpty @Size(max = 16) List<@NotNull @Valid Item> items) {

    public record Item(
            @NotNull @Positive @JsonDeserialize(using = WholeNumberDeserializer.class) Long partId,
            @NotNull @Min(1) @Max(100) @JsonDeserialize(using = WholeNumberDeserializer.class) Long quantity) {
    }

    // 이 요청에서만 소수/문자열의 자동 정수 변환을 막는다. 공통 JSON 설정은 유지한다.
    public static class WholeNumberDeserializer extends ValueDeserializer<Long> {
        @Override
        public Long deserialize(JsonParser parser, DeserializationContext context) throws JacksonException {
            if (!parser.hasToken(JsonToken.VALUE_NUMBER_INT)) {
                return (Long) context.handleUnexpectedToken(Long.class, parser);
            }
            return parser.getLongValue();
        }
    }
}
