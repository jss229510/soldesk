package com.comcheck.comcheck.domain.Board.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Table(name="BOARD")
@Entity 
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED) // 빈 글 생성 방지
public class Board {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "board_seq_generator")
    @SequenceGenerator(
            name = "board_seq_generator", // Java 안에서 부르는 이름
            sequenceName = "BOARD_SEQ",   // Oracle 시퀀스 이름
            allocationSize = 1) 
    @Column(name = "BOARD_ID")        
    private Long boardId; //글번호

    // 작성자(글 여러개: 회원 한명)
    // @ManyToOne: 1:N
    // @fetch = FetchType.Lazy: 실제 사용할 때 DB에서 가져옴
    // @JoinColumn: Member table과 조인  

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "MEMBER_ID")
    private Member writer;

    @Enumerated(EnumType.STRING) // 예: enum에 있던 이름 CAFE 글자로 지정
    @Column(name="CATEGORY")
    private Category category;
    
    @Column(name = "TITLE")
    private String title; // 제목

    @Column(name = "CONTENT")
    private String content; // 내용

    @Column(name = "VIEW_COUNT")
    private long viewCount; // Not Null 이고 0이 기본값이므로 정수형 long 사용

    @Column(name = "CREATED_AT")
    private LocalDateTime createdAt; // 작성 일시

    @Column(name = "UPDATED_AT")
    private LocalDateTime updatedAt; // 마지막 수정 일시

    // boardID는 저장할 때 자동으로 시퀀스가 채워짐
    public Board(Member writer, Category category, String title, String content) {
        this.writer = writer;
        this.category = category;
        this.title = title;
        this.content = content;
        this.viewCount = 0;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt; // 처음에는 작성 일시 = 수정 일시
    }

    // 수정할 때 setter 대신 수정 메서드 사용
    public void update(Category category, String title, String content) {
        this.category = category;
        this.title = title;
        this.content = content;
        this.updatedAt = LocalDateTime.now(); // 수정 일시 갱신
    }

    // 조회수 1씩 증가(update 시에는 조회수 증가 안함)
    public void increaseViewCount(){
        this.viewCount=this.viewCount+1;
    }

    // 이 글의 작성자가 memberId 회원인지를 확인(수정, 삭제시 권한 확인에 사용)
    // Long Type끼리 비교할 때는 == 이 아니고 equals()를 사용
    public boolean isWrittenBy(Long memberId) {
        return writer.getMemberId().equals(memberId);
    }
}

