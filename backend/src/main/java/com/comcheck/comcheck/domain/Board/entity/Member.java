package com.comcheck.comcheck.domain.Board.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity 
@Table(name="MEMBER")
@Getter 
// 기본생성자(즉 매개변수 없는 생성자)를 자동으로 선언해줌
@NoArgsConstructor(access = AccessLevel.PROTECTED)

public class Member {

    @Id // 이 필드가 기본키(primary key)이다
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "member_seq_generator")
    @SequenceGenerator(
        name = "member_seq_generator",
        sequenceName = "MEMBER_SEQ",
        allocationSize = 1)
    @Column(name = "MEMBER_ID") // 연결할 컬럼
    private Long memberId;

    @Column(name = "USERNAME") // 아이디
    private String username;

    @Column(name = "PASSWORD") // 암호화
    private String password;

    @Column(name = "NAME")
    private String name;

    @Column(name = "EMAIL")
    private String email;

    @Column(name = "CREATED_AT")
    private LocalDateTime createdAt;


    public Member(String username, String password, String name, String email) {
        this.username = username;
        this.password = password;
        this.name = name;
        this.email = email;
        this.createdAt = LocalDateTime.now(); //현재 날짜와 시간
    }


}

