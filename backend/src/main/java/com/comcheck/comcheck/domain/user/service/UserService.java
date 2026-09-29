package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import com.comcheck.comcheck.domain.user.dto.LoginRequest;
import com.comcheck.comcheck.domain.user.dto.LoginResponse;
import com.comcheck.comcheck.domain.user.dto.PasswordChangeRequest;

import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
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
        // 해싱 전에 필수 값을 검사해 불완전한 계정이 DB에 들어가지 않게 한다.
        if (user.getEmail() == null || user.getEmail().isBlank()
                || user.getPassword() == null || user.getPassword().isBlank()
                || user.getNickname() == null || user.getNickname().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "이메일, 비밀번호, 닉네임은 필수입니다.");
        }

        String email = user.getEmail().trim();
        String nickname = user.getNickname().trim();
        // 애플리케이션은 명확한 오류를 주고, DB UNIQUE 제약은 동시 요청 경쟁 상태를 막는다.
        if (userRepository.existsByEmail(email)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 사용 중인 이메일입니다.");
        }
        if (userRepository.existsByNickname(nickname)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 사용 중인 닉네임입니다.");
        }

        user.setEmail(email);
        user.setNickname(nickname);
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        user.setCreatedAt(LocalDateTime.now());
        return userRepository.save(user);
    }

    // 로그인
    public LoginResponse login(LoginRequest request) {
        // 누락된 인증 정보는 잘못된 요청이고, 틀린 이메일·비밀번호는 같은 오류로 처리한다.
        if (request.email() == null || request.email().isBlank()
                || request.password() == null || request.password().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "이메일과 비밀번호는 필수입니다.");
        }

        User user = userRepository.findByEmail(request.email().trim())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다."));

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다.");
        }

        // 로그인 응답에는 비밀번호나 비밀번호 해시를 절대 반환하지 않는다.
        return new LoginResponse(
                jwtTokenProvider.createToken(user.getUserId()),
                user.getUserId(),
                user.getEmail(),
                user.getNickname()
        );
    }

    @Transactional
    public void changePassword(Long userId, PasswordChangeRequest request) {
        // 입력 형식을 먼저 검사해 잘못된 비밀번호 변경 요청을 차단한다.
        if (request.currentPassword() == null || request.currentPassword().isBlank()
                || request.newPassword() == null || request.newPassword().length() < 8) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "현재 비밀번호와 8자 이상의 새 비밀번호가 필요합니다.");
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));

        // 기존 비밀번호는 저장된 BCrypt 해시와 비교하고 평문과 비교하지 않는다.
        if (!passwordEncoder.matches(request.currentPassword(), user.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "현재 비밀번호가 올바르지 않습니다.");
        }

        // 새 비밀번호도 BCrypt 해시로 바꾼 뒤 저장한다.
        user.setPassword(passwordEncoder.encode(request.newPassword()));
        userRepository.save(user);
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
    @Transactional
    public void deleteUser(Long userId){
        // Spring Data의 삭제 작업에는 활성화된 DB 트랜잭션이 필요하다.
        userRepository.deleteByUserId(userId);
    }

}
