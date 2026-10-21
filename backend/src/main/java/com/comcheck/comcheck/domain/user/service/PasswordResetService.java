package com.comcheck.comcheck.domain.user.service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.HexFormat;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.mail.MailException;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import com.comcheck.comcheck.domain.user.entity.PasswordResetToken;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.PasswordResetTokenRepository;
import com.comcheck.comcheck.domain.user.repository.UserRepository;

@Service
public class PasswordResetService {

    private static final Logger log = LoggerFactory.getLogger(PasswordResetService.class);
    private static final int TOKEN_BYTE_LENGTH = 32;

    private final UserRepository userRepository;
    private final PasswordResetTokenRepository tokenRepository;
    private final ObjectProvider<JavaMailSender> mailSenderProvider;
    private final PasswordEncoder passwordEncoder;
    private final SecureRandom secureRandom = new SecureRandom();
    private final String mailFrom;
    private final String frontendUrl;

    public PasswordResetService(
            UserRepository userRepository,
            PasswordResetTokenRepository tokenRepository,
            ObjectProvider<JavaMailSender> mailSenderProvider,
            PasswordEncoder passwordEncoder,
            @Value("${app.password-reset.from:}") String mailFrom,
            @Value("${app.password-reset.frontend-url:http://localhost:5173}") String frontendUrl) {
        this.userRepository = userRepository;
        this.tokenRepository = tokenRepository;
        this.mailSenderProvider = mailSenderProvider;
        this.passwordEncoder = passwordEncoder;
        this.mailFrom = mailFrom;
        this.frontendUrl = frontendUrl.replaceAll("/+$", "");
    }

    /**
     * 가입된 이메일이면 15분 동안 한 번 사용할 수 있는 비밀번호 재설정 링크를 발송한다.
     * 가입 여부가 응답 차이로 노출되지 않도록 존재하지 않는 이메일도 정상 종료한다.
     */
    @Transactional
    public void requestResetEmail(String email) {
        JavaMailSender mailSender = mailSenderProvider.getIfAvailable();
        if (mailSender == null || mailFrom.isBlank()) {
            throw new ResponseStatusException(
                    HttpStatus.SERVICE_UNAVAILABLE,
                    "비밀번호 재설정 메일 설정이 필요합니다.");
        }

        User foundUser = userRepository.findByEmail(email.trim()).orElse(null);
        if (foundUser == null) {
            return;
        }

        // 회원 행을 잠가 동시에 발급된 두 링크 중 어느 것이 유효한지 뒤바뀌지 않게 한다.
        User user = userRepository.findForPasswordReset(foundUser.getUserId()).orElse(null);
        if (user == null) {
            return;
        }

        LocalDateTime now = LocalDateTime.now();
        PasswordResetToken previousToken = tokenRepository.findById(user.getUserId()).orElse(null);
        if (previousToken != null && previousToken.getRequestedAt().plusMinutes(1).isAfter(now)) {
            return;
        }

        String rawToken = createRawToken();
        tokenRepository.save(new PasswordResetToken(user.getUserId(), hash(rawToken), now));

        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(mailFrom);
        message.setTo(user.getEmail());
        message.setSubject("[PartZone] 비밀번호 재설정");
        message.setText("아래 링크에서 새 비밀번호를 입력해주세요.\n"
                + "이 링크는 15분 동안 한 번만 사용할 수 있습니다.\n\n"
                + frontendUrl + "/reset-password#token=" + rawToken
                + "\n\n요청하지 않았다면 이 메일을 무시해주세요.");

        try {
            mailSender.send(message);
        } catch (MailException exception) {
            // 민감한 토큰과 메일 본문은 로그에 남기지 않는다. 예외 발생으로 토큰 저장도 롤백된다.
            log.warn("비밀번호 재설정 메일 발송 실패: {}", exception.getClass().getSimpleName());
            throw new ResponseStatusException(
                    HttpStatus.SERVICE_UNAVAILABLE,
                    "비밀번호 재설정 메일을 보내지 못했습니다.");
        }
    }

    /** 유효한 일회용 토큰을 소비한 뒤 BCrypt로 인코딩한 새 비밀번호를 저장한다. */
    @Transactional
    public void resetPassword(String rawToken, String newPassword) {
        String tokenHash = hash(rawToken);
        PasswordResetToken token = tokenRepository.findByTokenHash(tokenHash)
                .orElseThrow(this::invalidTokenException);

        User user = userRepository.findForPasswordReset(token.getUserId())
                .orElseThrow(this::invalidTokenException);

        int consumedCount = tokenRepository.consume(
                user.getUserId(),
                tokenHash,
                LocalDateTime.now());
        if (consumedCount != 1) {
            throw invalidTokenException();
        }

        user.changePassword(passwordEncoder.encode(newPassword));
    }

    private String createRawToken() {
        byte[] tokenBytes = new byte[TOKEN_BYTE_LENGTH];
        secureRandom.nextBytes(tokenBytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(tokenBytes);
    }

    private String hash(String rawToken) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(rawToken.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (NoSuchAlgorithmException exception) {
            throw new IllegalStateException("SHA-256을 사용할 수 없습니다.", exception);
        }
    }

    private ResponseStatusException invalidTokenException() {
        return new ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                "만료되었거나 사용할 수 없는 비밀번호 재설정 링크입니다.");
    }
}
