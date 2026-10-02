package com.comcheck.comcheck.domain.user.controller;

import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.dto.LoginRequest;
import com.comcheck.comcheck.domain.user.dto.LoginResponse;
import com.comcheck.comcheck.domain.user.dto.PasswordChangeRequest;
import com.comcheck.comcheck.domain.user.service.UserService;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 사용자 ID로 한 명 조회
    @GetMapping("/{userId}")
    public ResponseEntity<User> getUserById(@PathVariable Long userId, Authentication authentication) {
        validateOwner(userId, authentication);
        // Service를 통해 해당 ID의 사용자를 조회
        User user = userService.getUserById(userId);

        // 사용자가 없으면 HTTP 404 Not Found 응답
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // 사용자가 있으면 HTTP 200 OK와 사용자 정보를 JSON으로 반환
        return ResponseEntity.ok(user);
    }

    @GetMapping("/me")
    public ResponseEntity<User> getCurrentUser(Authentication authentication) {
        // 사용자 ID는 클라이언트 입력이 아니라 검증된 JWT에서 가져온다.
        Long userId = getAuthenticatedUserId(authentication);
        User user = userService.getUserById(userId);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok(user);
    }

    @PutMapping("/me/password")
    public ResponseEntity<Void> changePassword(
            @RequestBody PasswordChangeRequest request,
            Authentication authentication
    ) {
        // 사용자 ID는 요청 본문이 아니라 검증된 JWT의 principal에서 가져온다.
        userService.changePassword(getAuthenticatedUserId(authentication), request);
        return ResponseEntity.noContent().build();
    }

    // 회원가입
    @PostMapping
    public ResponseEntity<User> saveUser(@RequestBody User user) {
        return ResponseEntity.status(HttpStatus.CREATED).body(userService.saveUser(user));
    }

    @PostMapping("/login")
    public ResponseEntity<LoginResponse> login(@RequestBody LoginRequest request) {
        return ResponseEntity.ok(userService.login(request));
    }

    // 이메일 중복 확인
    @GetMapping("/check-email")
    public boolean checkEmail(@RequestParam String email) {
        return userService.isEmailDuplicate(email);
    }

    // 닉네임 중복 확인
    @GetMapping("/check-nickname")
    public boolean checkNickname(@RequestParam String nickname) {
        return userService.isNicknameDuplicate(nickname);
    }

    // 사용자 ID로 회원 탈퇴
    @DeleteMapping("/{userId}")
    public ResponseEntity<Void> deleteByUserId(@PathVariable Long userId, Authentication authentication) {
        validateOwner(userId, authentication);
        // 삭제 전에 사용자가 존재하는지 확인
        User user = userService.getUserById(userId);

        // 존재하지 않는 사용자면 HTTP 404 Not Found 응답
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // 존재하는 사용자만 삭제
        userService.deleteUser(userId);

        // 삭제 성공 시 HTTP 204 No Content 응답
        return ResponseEntity.noContent().build();
    }

    private Long getAuthenticatedUserId(Authentication authentication) {
        // JwtAuthenticationFilter가 숫자 사용자 ID를 현재 요청의 principal에 저장한다.
        if (authentication == null || !(authentication.getPrincipal() instanceof Long userId)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "유효한 로그인 정보가 필요합니다.");
        }

        return userId;
    }

    private void validateOwner(Long userId, Authentication authentication) {
        // 인증은 신원을 확인하고, 이 비교는 본인 소유 권한을 강제한다.
        if (!userId.equals(getAuthenticatedUserId(authentication))) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인 계정만 조회하거나 탈퇴할 수 있습니다.");
        }
    }
}
