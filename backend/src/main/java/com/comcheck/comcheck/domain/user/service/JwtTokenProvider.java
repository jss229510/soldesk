package com.comcheck.comcheck.domain.user.service;

import org.springframework.stereotype.Component;
import io.jsonwebtoken.Jwts;
import java.util.Date;

import java.time.Instant;

import javax.crypto.SecretKey;

@Component
public class JwtTokenProvider {
    // 서버가 실행되는 동안 같은 키를 사용하며, 재시작하면 기존 토큰은 무효가 된다.
    private final SecretKey key = Jwts.SIG.HS256.key().build();

    public String createToken(Long userId) {
        Instant now = Instant.now();

        // 사용자 ID를 토큰의 주체로 저장하고, 서명된 토큰은 1시간 뒤 만료한다.
        return Jwts.builder()
        .subject(userId.toString())
        .issuedAt(Date.from(now))
        .expiration(Date.from(now.plusSeconds(3600)))
        .signWith(key)
        .compact();
    }
}
