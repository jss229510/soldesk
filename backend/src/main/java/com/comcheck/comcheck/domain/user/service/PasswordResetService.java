package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.entity.PasswordResetToken;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.PasswordResetTokenRepository;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.MailException;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.HexFormat;

@Service
public class PasswordResetService {
    private static final Logger log = LoggerFactory.getLogger(PasswordResetService.class);
    private final UserRepository userRepository;
    private final PasswordResetTokenRepository tokenRepository;
    private final ObjectProvider<JavaMailSender> mailSender;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();
    private final SecureRandom random = new SecureRandom();
    private final String from;
    private final String frontendUrl;

    public PasswordResetService(UserRepository userRepository,
            PasswordResetTokenRepository tokenRepository, ObjectProvider<JavaMailSender> mailSender,
            @Value("${app.password-reset.from:}") String from,
            @Value("${app.password-reset.frontend-url:http://localhost:5173}") String frontendUrl) {
        this.userRepository = userRepository;
        this.tokenRepository = tokenRepository;
        this.mailSender = mailSender;
        this.from = from;
        this.frontendUrl = frontendUrl.replaceAll("/+$", "");
    }

    // 재설정 메일 발송
    @Transactional
    public void requestEmail(String email) {
        // 이메일 형식 확인
        if (email == null || email.length() > 255
                || !email.trim().matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "이메일을 확인해주세요.");
        }
        JavaMailSender sender = mailSender.getIfAvailable();
        if (sender == null || from.isBlank()) {
            log.warn("메일 발송 설정 누락: MAIL_NOT_CONFIGURED");
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "메일 설정이 필요합니다.");
        }

        // 가입 여부는 응답으로 알려주지 않음
        User found = userRepository.findByEmail(email.trim()).orElse(null);
        if (found == null) {
            return;
        }
        User user = userRepository.findForPasswordReset(found.getUserId()).orElse(null);
        if (user == null) {
            return;
        }

        LocalDateTime now = LocalDateTime.now();
        PasswordResetToken previous = tokenRepository.findById(user.getUserId()).orElse(null);
        // 1분 이내 재발송 방지
        if (previous != null && previous.getRequestedAt().plusMinutes(1).isAfter(now)) {
            return;
        }

        byte[] bytes = new byte[32];
        random.nextBytes(bytes);
        String token = Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
        // 토큰은 해시로 저장. 재발급하면 이전 링크는 사용할 수 없음
        tokenRepository.save(new PasswordResetToken(user.getUserId(), hash(token), now));
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(from);
        message.setTo(user.getEmail());
        message.setSubject("[PartZone] 비밀번호 재설정");
        message.setText("아래 링크에서 새 비밀번호를 입력해주세요.\n15분 동안 한 번 사용할 수 있습니다.\n\n"
                + frontendUrl + "/reset-password#token=" + token
                + "\n\n요청하지 않으셨다면 이 메일을 무시해주세요.");
        // 발송 실패 시 토큰 저장도 취소
        try {
            sender.send(message);
        } catch (MailException exception) {
            // 비밀번호와 메일 본문 없이 오류 종류만 기록
            log.warn("메일 발송 실패: 종류={}, 원인={}",
                    exception.getClass().getSimpleName(),
                    exception.getMostSpecificCause().getClass().getSimpleName());
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE, "메일 발송에 실패했습니다.");
        }
    }

    // 토큰 확인 후 비밀번호 변경
    @Transactional
    public void resetPassword(String token, String newPassword) {
        // 새 비밀번호 확인
        if (newPassword == null || newPassword.isBlank() || newPassword.length() < 8
                || newPassword.getBytes(StandardCharsets.UTF_8).length > 72) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "비밀번호는 8자 이상, 72바이트 이내로 입력해주세요.");
        }
        if (token == null || !token.matches("[A-Za-z0-9_-]{43}")) {
            throw invalidLink();
        }
        String tokenHash = hash(token);
        PasswordResetToken found = tokenRepository.findByTokenHash(tokenHash).orElseThrow(this::invalidLink);
        User user = userRepository.findForPasswordReset(found.getUserId()).orElseThrow(this::invalidLink);
        // 만료와 중복 사용 확인. 비밀번호 저장 실패 시 삭제도 취소
        if (tokenRepository.consume(user.getUserId(), tokenHash, LocalDateTime.now()) != 1) {
            throw invalidLink();
        }
        // 새 비밀번호는 BCrypt 해시로 저장
        int updated = userRepository.updatePasswordForReset(user.getUserId(), passwordEncoder.encode(newPassword));
        if (updated != 1) {
            throw invalidLink();
        }
    }

    private ResponseStatusException invalidLink() {
        return new ResponseStatusException(HttpStatus.BAD_REQUEST, "만료되었거나 사용할 수 없는 링크입니다.");
    }

    // 링크 토큰을 DB에 저장할 해시로 변환
    private String hash(String token) {
        try {
            return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256")
                    .digest(token.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException(exception);
        }
    }
}
