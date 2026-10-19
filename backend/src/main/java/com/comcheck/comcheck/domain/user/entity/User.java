package com.comcheck.comcheck.domain.user.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.PrePersist;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@Entity
@Table(name = "USERS")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "usersSequence")
    @SequenceGenerator(name = "usersSequence", sequenceName = "SEQ_USERS", allocationSize = 1)
    @Column(name = "\"user_id\"")
    private Long userId;

    @Column(name = "\"email\"")
    private String email;

    @Column(name = "\"password\"")
    private String password;

    @Column(name = "\"nickname\"")
    private String nickname;

    @Column(name = "\"phone_number\"")
    private String phoneNumber;

    @Column(name = "\"created_at\"")
    private LocalDateTime createdAt;

    // JPA가 DB 행을 Entity로 복원할 때 사용하는 기본 생성자다.
    protected User() {
    }

    // password에는 Service에서 BCrypt로 인코딩한 값만 전달한다.
    public User(String email, String encodedPassword, String nickname) {
        this.email = email;
        this.password = encodedPassword;
        this.nickname = nickname;
    }

    @PrePersist
    private void setCreatedAtIfAbsent() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }

    public void changePassword(String encodedPassword) {
        this.password = encodedPassword;
    }

    public Long getUserId() {
        return userId;
    }

    public String getEmail() {
        return email;
    }

    public String getPassword() {
        return password;
    }

    public String getNickname() {
        return nickname;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
