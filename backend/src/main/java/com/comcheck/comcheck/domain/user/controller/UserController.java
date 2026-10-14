package com.comcheck.comcheck.domain.user.controller;

import com.comcheck.comcheck.domain.user.dto.LoginRequest;
import com.comcheck.comcheck.domain.user.dto.LoginResponse;
import com.comcheck.comcheck.domain.user.dto.PasswordChangeRequest;
import com.comcheck.comcheck.domain.user.dto.SignupRequest;
import com.comcheck.comcheck.domain.user.dto.UserResponse;
import com.comcheck.comcheck.domain.user.service.UserService;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{userId}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long userId, Authentication authentication) {
        validateOwner(userId, authentication);
        return ResponseEntity.ok(userService.getUserById(userId));
    }

    @GetMapping("/me")
    public ResponseEntity<UserResponse> getCurrentUser(Authentication authentication) {
        return ResponseEntity.ok(userService.getUserById(getAuthenticatedUserId(authentication)));
    }

    @PutMapping("/me/password")
    public ResponseEntity<Void> changePassword(
            @RequestBody PasswordChangeRequest request,
            Authentication authentication
    ) {
        userService.changePassword(getAuthenticatedUserId(authentication), request);
        return ResponseEntity.noContent().build();
    }

    @PostMapping
    public ResponseEntity<UserResponse> signup(@Valid @RequestBody SignupRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(userService.signup(request));
    }

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(userService.login(request));
    }

    @GetMapping("/check-email")
    public boolean checkEmail(@RequestParam String email) {
        return userService.isEmailDuplicate(email);
    }

    @GetMapping("/check-nickname")
    public boolean checkNickname(@RequestParam String nickname) {
        return userService.isNicknameDuplicate(nickname);
    }

    @DeleteMapping("/{userId}")
    public ResponseEntity<Void> deleteByUserId(@PathVariable Long userId, Authentication authentication) {
        validateOwner(userId, authentication);
        userService.deleteUser(userId);
        return ResponseEntity.noContent().build();
    }

    private Long getAuthenticatedUserId(Authentication authentication) {
        if (authentication == null || !(authentication.getPrincipal() instanceof Long userId)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "유효한 로그인 정보가 필요합니다.");
        }
        return userId;
    }

    private void validateOwner(Long userId, Authentication authentication) {
        if (!userId.equals(getAuthenticatedUserId(authentication))) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인 계정만 조회하거나 탈퇴할 수 있습니다.");
        }
    }
}
