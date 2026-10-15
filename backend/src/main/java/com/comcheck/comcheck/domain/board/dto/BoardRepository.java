package com.comcheck.comcheck.domain.board.dto;

import com.comcheck.comcheck.domain.board.entity.Category;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter 
@Setter 
@NoArgsConstructor 
public class BoardRepository {
    @NotNull (message = "카테고리를 선택하세요.")
    private Category category;

    @NotBlank (message = "제목을 입력하세요")
    private String title;

    @NotBlank (message = "내용을 입력하세요")
    @Size (max = 1000, message = "내용은 1000자 이하로 입력하세요")
    private String content;
}
