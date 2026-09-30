package com.comcheck.comcheck.domain.user.entity;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonProperty;

@Entity
@Table(name = "USERS")
public class User {
    @Id
    // Oracle이 SEQ_USERS로 ID를 생성하므로 클라이언트가 사용자 ID를 직접 정할 수 없다.
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "usersSequence")
    @SequenceGenerator(name = "usersSequence", sequenceName = "SEQ_USERS", allocationSize = 1)

    @Column(name = "\"user_id\"")
    private Long userId;

    @Column(name = "\"email\"")
    private String email;
    
    @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
    @Column(name = "\"password\"")
    private String password;

    @Column(name = "\"nickname\"")
    private String nickname;

    @Column(name = "\"phone_number\"")
    private String phoneNumber;

    @Column(name = "\"created_at\"")
    private java.time.LocalDateTime createdAt;

    public Long getUserId() {
        return userId;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        // Service의 유효성 검사 전에 JSON 회원가입 요청을 받기 위해 필요하다.
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getNickname() {
        return nickname;
    }

    public void setNickname(String nickname) {
        this.nickname = nickname;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public java.time.LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(java.time.LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
