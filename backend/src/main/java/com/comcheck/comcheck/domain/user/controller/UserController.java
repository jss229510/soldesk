package com.comcheck.comcheck.domain.user.controller;

import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.service.UserService;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    // 전체 사용자 조회
    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }

    // 사용자 ID로 한 명 조회
    @GetMapping("/{userId}")
    public ResponseEntity<User> getUserById(@PathVariable Long userId) {
        // Service를 통해 해당 ID의 사용자를 조회
        User user = userService.getUserById(userId);

        // 사용자가 없으면 HTTP 404 Not Found 응답
        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // 사용자가 있으면 HTTP 200 OK와 사용자 정보를 JSON으로 반환
        return ResponseEntity.ok(user);
    }

    // 회원가입
    @PostMapping
    public User saveUser(@RequestBody User user) {
        return userService.saveUser(user);
    }

    // 로그인 정보를 서비스에 전달하고 성공하면 JWT 문자열을 반환한다.
    @PostMapping("/login")
    public String login(@RequestParam String email,
            @RequestParam String password) {
        return userService.login(email, password);
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
    public ResponseEntity<Void> deleteByUserId(@PathVariable Long userId) {
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
}
