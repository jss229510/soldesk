package com.comcheck.comcheck.domain.build.dto;

import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;

public record ReplacementRequest(
        @NotBlank(message = "용도가 필요합니다.")
        @Size(max = 30, message = "용도는 30자 이하여야 합니다.")
        String usageType,

        @NotBlank(message = "세부 등급이 필요합니다.")
        @Size(max = 40, message = "세부 등급은 40자 이하여야 합니다.")
        String tierCode,

        @NotBlank(message = "교체할 부품 종류가 필요합니다.")
        @Pattern(
                regexp = "(?i)(CPU|GPU|RAM|SSD|MAINBOARD|PSU"
                        + "|CASE|COOLER)",
                message = "지원하지 않는 교체 부품 종류입니다."
        )
        String category,

        @NotEmpty(message = "현재 구성이 필요합니다.")
        @Size(max = 8, message = "구성 품목은 최대 8개입니다.")
        List<
                @NotNull(message = "빈 품목은 허용하지 않습니다.")
                @Valid SelectedPart
        > items) {

    public record SelectedPart(
            @NotNull(message = "제품 번호가 필요합니다.")
            @Positive(message = "제품 번호는 양수여야 합니다.")
            Long partId,

            @NotNull(message = "수량이 필요합니다.")
            @Positive(message = "수량은 양수여야 합니다.")
            Long quantity) {
    }
}
