package com.comcheck.comcheck.domain.user.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "USERS")
public class User {
    @Id

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
    private java.time.LocalDateTime createdAt;

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

    public java.time.LocalDateTime getCreatedAt() {
        return createdAt;
    }
}