package com.comcheck.comcheck.config;

import com.comcheck.comcheck.domain.user.security.JwtAuthenticationFilter;
import com.comcheck.comcheck.global.exception.SecurityErrorResponseWriter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import java.util.List;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

        @Bean
        PasswordEncoder passwordEncoder() {
                return new BCryptPasswordEncoder();
        }

        @Bean
        SecurityFilterChain securityFilterChain(
                        HttpSecurity http,
                        JwtAuthenticationFilter jwtAuthenticationFilter,
                        SecurityErrorResponseWriter securityErrorResponseWriter)
                        throws Exception {
                return http
                                // 이 API는 토큰 기반이므로 HTTP 세션을 만들지 않는다.
                                .csrf(csrf -> csrf.disable())
                                .cors(Customizer.withDefaults())
                                .sessionManagement(session -> session
                                                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                                .exceptionHandling(exception -> exception
                                                .authenticationEntryPoint((request, response,
                                                                authException) -> securityErrorResponseWriter.write(
                                                                                response, HttpStatus.UNAUTHORIZED,
                                                                                "로그인이 필요합니다."))
                                                .accessDeniedHandler((request, response,
                                                                accessDeniedException) -> securityErrorResponseWriter
                                                                                .write(response, HttpStatus.FORBIDDEN,
                                                                                                "접근 권한이 없습니다.")))
                                .authorizeHttpRequests(authorize -> authorize
                                                // 로그인, 회원가입, 상품 조회는 인증 전에도 사용할 수 있어야 한다.
                                                .requestMatchers("/error").permitAll()
                                                .requestMatchers(HttpMethod.POST, "/api/users", "/api/users/login")
                                                .permitAll()
                                                .requestMatchers(HttpMethod.POST,
                                                                "/api/users/forgot-password",
                                                                "/api/users/reset-password")
                                                .permitAll()
                                                .requestMatchers(HttpMethod.GET, "/api/users/check-email",
                                                                "/api/users/check-nickname")
                                                .permitAll()
                                                .requestMatchers(HttpMethod.GET, "/api/parts/**").permitAll()
                                                .requestMatchers(HttpMethod.GET, "/api/boards", "/api/boards/**")
                                                .permitAll()
                                                .requestMatchers(HttpMethod.GET, "/uploads/boards/**").permitAll()
                                                .requestMatchers(HttpMethod.GET, "/api/estimates/recommended",
                                                                "/api/estimates/recommended/budget", "/api/estimates/*",
                                                                "/api/estimates/*/power-check")
                                                .permitAll()
                                                // 항목 조회는 서비스에서 추천 견적 여부와 개인 견적의 소유자를 검사한다.
                                                .requestMatchers(HttpMethod.GET, "/api/estimates/*/items").permitAll()
                                                .requestMatchers(HttpMethod.POST, "/api/build/replacements")
                                                .permitAll()
                                                .requestMatchers(HttpMethod.POST, "/api/estimates/power-check").permitAll()
                                                .anyRequest().authenticated())
                                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
                                .build();
        }

        @Bean
        CorsConfigurationSource corsConfigurationSource() {
                // Vite 개발 서버가 JSON과 Authorization 헤더를 보낼 수 있게 허용한다.
                CorsConfiguration configuration = new CorsConfiguration();
                configuration.setAllowedOrigins(List.of(
                                "http://localhost:5173", "http://127.0.0.1:5173"));
                configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
                configuration.setAllowedHeaders(List.of("Authorization", "Content-Type"));

                UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
                source.registerCorsConfiguration("/**", configuration);
                return source;
        }
}
