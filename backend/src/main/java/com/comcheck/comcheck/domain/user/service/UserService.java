package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.dto.LoginRequest;
import com.comcheck.comcheck.domain.user.dto.LoginResponse;
import com.comcheck.comcheck.domain.user.dto.PasswordChangeRequest;
import com.comcheck.comcheck.domain.user.dto.SignupRequest;
import com.comcheck.comcheck.domain.user.dto.UserResponse;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    public UserService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtTokenProvider jwtTokenProvider
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenProvider = jwtTokenProvider;
    }

    @Transactional
    public UserResponse signup(SignupRequest request) {
        String email = request.email().trim();
        String nickname = request.nickname().trim();

        if (userRepository.existsByEmail(email)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 사용 중인 이메일입니다.");
        }
        if (userRepository.existsByNickname(nickname)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "이미 사용 중인 닉네임입니다.");
        }

        String encodedPassword = passwordEncoder.encode(request.password());
        User savedUser = userRepository.save(new User(email, encodedPassword, nickname));
        return UserResponse.from(savedUser);
    }

    public UserResponse getUserById(Long userId) {
        return UserResponse.from(findUserById(userId));
    }

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.email().trim())
                .orElseThrow(() -> invalidLoginException());

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw invalidLoginException();
        }

        return new LoginResponse(
                jwtTokenProvider.createToken(user.getUserId()),
                user.getUserId(),
                user.getEmail(),
                user.getNickname()
        );
    }

    @Transactional
    public void changePassword(Long userId, PasswordChangeRequest request) {
        if (request.currentPassword() == null || request.currentPassword().isBlank()
                || request.newPassword() == null || request.newPassword().length() < 8) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "현재 비밀번호와 8자 이상의 새 비밀번호가 필요합니다.");
        }

        User user = findUserById(userId);
        if (!passwordEncoder.matches(request.currentPassword(), user.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "현재 비밀번호가 올바르지 않습니다.");
        }

        user.changePassword(passwordEncoder.encode(request.newPassword()));
    }

    public boolean isEmailDuplicate(String email) {
        return email != null && userRepository.existsByEmail(email.trim());
    }

    public boolean isNicknameDuplicate(String nickname) {
        return nickname != null && userRepository.existsByNickname(nickname.trim());
    }

    @Transactional
    public void deleteUser(Long userId) {
        userRepository.delete(findUserById(userId));
    }

    private User findUserById(Long userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "사용자를 찾을 수 없습니다."));
    }

    private ResponseStatusException invalidLoginException() {
        return new ResponseStatusException(HttpStatus.UNAUTHORIZED, "이메일 또는 비밀번호가 올바르지 않습니다.");
    }
}
