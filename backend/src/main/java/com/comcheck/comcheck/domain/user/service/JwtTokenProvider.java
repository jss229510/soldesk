package com.comcheck.comcheck.domain.user.service;

import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import io.jsonwebtoken.io.Decoders;
import java.util.Date;

import java.time.Instant;

import javax.crypto.SecretKey;

@Component
public class JwtTokenProvider {
    private final SecretKey key;

    public JwtTokenProvider(@Value("${jwt.secret}") String secret) {
        // Base64 비밀 키는 환경 변수에서 주입하며 서버 재시작마다 새로 만들지 않는다.
        this.key = Keys.hmacShaKeyFor(Decoders.BASE64.decode(secret));
    }

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

    public Long getUserId(String token) {
        // 토큰을 파싱하는 과정에서 서명과 만료 시간을 함께 검증한다.
        String subject = Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload()
                .getSubject();

        return Long.valueOf(subject);
    }
}
