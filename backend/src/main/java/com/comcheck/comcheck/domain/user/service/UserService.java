package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;


import java.util.List;

@Service
public class UserService {

    private final UserRepository  userRepository;
    private final PasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    private final JwtTokenProvider jwtTokenProvider;

    public UserService(UserRepository userRepository, JwtTokenProvider jwtTokenProvider) {
        this.userRepository = userRepository;
        this.jwtTokenProvider=jwtTokenProvider;
    }

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    public User getUserById(Long userId) {
        return userRepository.findById(userId)
                .orElse(null);
    }

    public User saveUser(User user) {
        if(user.getPassword() == null || user.getPassword().isBlank()){
            throw new IllegalArgumentException("Password is required");
        }
        // 원문 비밀번호를 저장하지 않고 BCrypt 해시로 바꿔 저장한다.
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        return userRepository.save(user);
    }

    // 로그인
    public String login(String email, String password) {
        User user = userRepository.findByEmail(email).orElse(null);
        // 사용자가 없거나 입력한 비밀번호가 저장된 해시와 맞지 않으면 실패한다.
        if (user == null || password == null || !passwordEncoder.matches(password, user.getPassword())) {
            return null;
        }
        // 비밀번호 검증을 통과한 사용자에게만 JWT를 발급한다.
        return jwtTokenProvider.createToken(user.getUserId());
    }

    // 이메일 중복 확인
    public boolean isEmailDuplicate(String email) {
        return userRepository.existsByEmail(email);
    }

    // 닉네임 중복 확인
    public boolean isNicknameDuplicate(String nickname) {
        return userRepository.existsByNickname(nickname);
    }

    // 전달받은 ID로 사용자를 삭제한다.
    public void deleteUser(Long userId){
        userRepository.deleteByUserId(userId);
    }

}
