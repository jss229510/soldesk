package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.repository.UserRepository;
import jakarta.mail.Session;
import jakarta.mail.internet.MimeMessage;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;

import java.io.*;
import java.net.*;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;
import java.util.regex.Pattern;
import static org.junit.jupiter.api.Assertions.*;

// 실제 HTTP, SMTP, 임시 DB를 사용. 운영 DB와 외부 메일에는 연결하지 않음
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, properties = {
        "spring.datasource.url=jdbc:h2:mem:password_reset_flow;MODE=Oracle;DB_CLOSE_DELAY=-1",
        "spring.datasource.driver-class-name=org.h2.Driver",
        "spring.datasource.username=sa", "spring.datasource.password=",
        "spring.jpa.hibernate.ddl-auto=create-drop", "spring.jpa.show-sql=false",
        "spring.mail.host=127.0.0.1", "spring.mail.username=", "spring.mail.password=",
        "spring.mail.properties.mail.smtp.auth=false",
        "spring.mail.properties.mail.smtp.starttls.enable=false",
        "spring.mail.properties.mail.smtp.starttls.required=false",
        "app.password-reset.from=sender@example.test"
})
class PasswordResetFlowTest {
    static final TestMailbox mailbox = new TestMailbox();
    @Value("${local.server.port}") int port;
    @Autowired UserRepository users;
    @Autowired JdbcTemplate jdbc;
    final HttpClient client = HttpClient.newHttpClient();

    @DynamicPropertySource
    static void properties(DynamicPropertyRegistry registry) {
        registry.add("spring.mail.port", () -> mailbox.server.getLocalPort());
        byte[] key = new byte[32];
        new SecureRandom().nextBytes(key);
        registry.add("jwt.secret", () -> Base64.getEncoder().encodeToString(key));
    }

    @AfterAll
    static void closeMailbox() throws Exception { mailbox.server.close(); }

    HttpResponse<String> post(String path, String json) throws Exception {
        return client.send(HttpRequest.newBuilder(URI.create("http://localhost:" + port + "/api/users" + path))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json)).build(), HttpResponse.BodyHandlers.ofString());
    }

    String requestLink(String email) throws Exception {
        assertEquals(204, post("/forgot-password", "{\"email\":\"" + email + "\"}").statusCode());
        String body = mailbox.messages.poll(5, TimeUnit.SECONDS);
        assertNotNull(body, "로컬 메일함에 메일이 도착해야 함");
        var matcher = Pattern.compile("#token=([A-Za-z0-9_-]{43})").matcher(body);
        assertTrue(matcher.find(), "메일에 재설정 링크가 있어야 함");
        return matcher.group(1);
    }

    String resetJson(String token) {
        return "{\"token\":\"" + token + "\",\"newPassword\":\"new-pass123\"}";
    }

    @Test
    void emailResetAndLogin() throws Exception {
        String email = "flow@example.test";
        assertEquals(201, post("", "{\"email\":\"" + email + "\",\"password\":\"old-pass123\",\"nickname\":\"flow-test\"}").statusCode());
        String token = requestLink(email);
        assertEquals(204, post("/reset-password", resetJson(token)).statusCode());
        String hash = users.findByEmail(email).orElseThrow().getPassword();
        assertNotEquals("new-pass123", hash);
        assertTrue(new BCryptPasswordEncoder().matches("new-pass123", hash));
        assertEquals(401, post("/login", "{\"email\":\"" + email + "\",\"password\":\"old-pass123\"}").statusCode());
        HttpResponse<String> login = post("/login", "{\"email\":\"" + email + "\",\"password\":\"new-pass123\"}");
        assertEquals(200, login.statusCode());
        assertTrue(login.body().contains("accessToken"));
        assertFalse(login.body().contains(hash));
        assertEquals(400, post("/reset-password", resetJson(token)).statusCode());
    }

    @Test
    void expiredAndReplacedLinksFail() throws Exception {
        String email = "expired@example.test";
        assertEquals(201, post("", "{\"email\":\"" + email + "\",\"password\":\"old-pass123\",\"nickname\":\"expired-test\"}").statusCode());
        String first = requestLink(email);
        Long userId = users.findByEmail(email).orElseThrow().getUserId();
        jdbc.update("update PASSWORD_RESET_TOKENS set REQUESTED_AT = ?, EXPIRES_AT = ? where USER_ID = ?",
                Timestamp.valueOf(LocalDateTime.now().minusMinutes(20)), Timestamp.valueOf(LocalDateTime.now().minusMinutes(5)), userId);
        assertEquals(400, post("/reset-password", resetJson(first)).statusCode());
        String second = requestLink(email);
        assertNotEquals(first, second);
        assertEquals(400, post("/reset-password", resetJson(first)).statusCode());
        assertEquals(204, post("/reset-password", resetJson(second)).statusCode());
    }

    // 테스트용 SMTP 수신기. 외부로 보내지 않고 메일 본문만 메모리에 보관
    static class TestMailbox {
        final ServerSocket server;
        final BlockingQueue<String> messages = new LinkedBlockingQueue<>();
        TestMailbox() {
            try { server = new ServerSocket(0, 10, InetAddress.getByName("127.0.0.1")); }
            catch (IOException exception) { throw new UncheckedIOException(exception); }
            Thread thread = new Thread(() -> {
                while (!server.isClosed()) {
                    try (Socket socket = server.accept()) { receive(socket); }
                    catch (Exception exception) { if (!server.isClosed()) throw new RuntimeException(exception); }
                }
            }, "test-mailbox");
            thread.setDaemon(true);
            thread.start();
        }
        void receive(Socket socket) throws Exception {
            socket.setSoTimeout(10000);
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream(), StandardCharsets.UTF_8));
            PrintWriter writer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream(), StandardCharsets.UTF_8), true);
            writer.print("220 localhost test mail\r\n"); writer.flush();
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.equalsIgnoreCase("DATA")) {
                    writer.print("354 send message\r\n"); writer.flush();
                    StringBuilder data = new StringBuilder();
                    while ((line = reader.readLine()) != null && !line.equals(".")) {
                        data.append(line.startsWith("..") ? line.substring(1) : line).append("\r\n");
                    }
                    MimeMessage message = new MimeMessage(Session.getInstance(new Properties()),
                            new ByteArrayInputStream(data.toString().getBytes(StandardCharsets.UTF_8)));
                    messages.add((String) message.getContent());
                    writer.print("250 received\r\n"); writer.flush();
                } else if (line.equalsIgnoreCase("QUIT")) {
                    writer.print("221 bye\r\n"); writer.flush(); return;
                } else {
                    writer.print("250 OK\r\n"); writer.flush();
                }
            }
        }
    }
}
