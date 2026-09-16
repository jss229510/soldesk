package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

import org.springframework.boot.webmvc.autoconfigure.WebMvcProperties.Apiversion.Use;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    public User getUserById(Long userId) {
        return userRepository.findById(userId)
                .orElse(null);
    }

    public User saveUser(User user) {
        return userRepository.save(user);
    }

    // 로그인
    public User login(String email, String password) {
        User user = userRepository.findByEmail(email).orElse(null);
        // 이메일이 없거나 비밀번호가 다르면 로그인 실패
        if (user == null || !user.getEmail().equals(password)) {
            return null;
        }
        return user;
    }

    // 이메일 중복 확인
    public boolean isEmailDuplicate(String email) {
        return userRepository.existsByEmail(email);
    }
}