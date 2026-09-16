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

    // 1번 사용자 조회
    @GetMapping("/{user_Id}")
    public User getUserById(@PathVariable Long userId) {
        return userService.getUserById(userId);
    }

    // 사용자 저장(회원가입)
    @PostMapping
    public User saveUser(@RequestBody User user) {
        return userService.saveUser(user);
    }

    // 사용자 로그인
    @PostMapping
    public User login(@RequestParam String email, @RequestParam String password) {
        return userService.login(email, password);
    }

    // 이메일 중복 확인
    @GetMapping("/check-email")
    public boolean checkEmail(@RequestParam String email) {
        return userService.isEmailDuplicate(email);
    }

}
