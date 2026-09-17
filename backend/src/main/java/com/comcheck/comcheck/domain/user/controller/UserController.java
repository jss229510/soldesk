package com.comcheck.comcheck.domain.user.controller;

import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.service.UserService;
import org.springframework.web.bind.annotation.*;

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

    // 사용자 한 명 조회
    @GetMapping("/{userId}")
    public User getUserById(@PathVariable Long userId) {
        return userService.getUserById(userId);
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

    // 경로의 사용자 ID로 탈퇴를 요청한다.
    @DeleteMapping("/{userId}")
    public void deleteByUserId(@PathVariable Long userId){
        userService.deleteUser(userId);
    }
}
