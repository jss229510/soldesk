package com.comcheck.comcheck.domain.user.service;

import com.comcheck.comcheck.domain.user.entity.PasswordResetToken;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.PasswordResetTokenRepository;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.mail.MailSendException;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.server.ResponseStatusException;
import java.time.LocalDateTime;
import java.util.Optional;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class PasswordResetServiceTest {
    private UserRepository users;
    private PasswordResetTokenRepository tokens;
    private JavaMailSender sender;
    private PasswordResetService service;
    private User user;
    private final String token = "A".repeat(43);

    @BeforeEach
    @SuppressWarnings("unchecked")
    void setUp() {
        users = mock(UserRepository.class);
        tokens = mock(PasswordResetTokenRepository.class);
        sender = mock(JavaMailSender.class);
        ObjectProvider<JavaMailSender> provider = mock(ObjectProvider.class);
        when(provider.getIfAvailable()).thenReturn(sender);
        service = new PasswordResetService(users, tokens, provider, "sender@example.test", "http://localhost:5173");
        user = mock(User.class);
        when(user.getUserId()).thenReturn(1L);
        when(user.getEmail()).thenReturn("member@example.test");
        when(users.findByEmail("member@example.test")).thenReturn(Optional.of(user));
        when(users.findForPasswordReset(1L)).thenReturn(Optional.of(user));
    }

    @Test
    void sendsLinkAndStoresOnlyHash() {
        service.requestEmail("member@example.test");
        ArgumentCaptor<PasswordResetToken> stored = ArgumentCaptor.forClass(PasswordResetToken.class);
        ArgumentCaptor<SimpleMailMessage> mail = ArgumentCaptor.forClass(SimpleMailMessage.class);
        verify(tokens).save(stored.capture());
        verify(sender).send(mail.capture());
        String raw = mail.getValue().getText().split("#token=")[1].split("\\n")[0];
        assertEquals(43, raw.length());
        assertEquals(64, stored.getValue().getTokenHash().length());
        assertNotEquals(raw, stored.getValue().getTokenHash());
        assertEquals(stored.getValue().getRequestedAt().plusMinutes(15), stored.getValue().getExpiresAt());
    }

    @Test
    void unknownEmailDoesNotSendMail() {
        when(users.findByEmail("unknown@example.test")).thenReturn(Optional.empty());
        service.requestEmail("unknown@example.test");
        verifyNoInteractions(sender, tokens);
    }

    @Test
    void waitsOneMinuteBeforeResending() {
        when(tokens.findById(1L)).thenReturn(Optional.of(new PasswordResetToken(1L, "hash", LocalDateTime.now())));
        service.requestEmail("member@example.test");
        verifyNoInteractions(sender);
        verify(tokens, never()).save(any());
    }

    @Test
    void mailFailureReturnsUnavailable() {
        doThrow(new MailSendException("test")).when(sender).send(any(SimpleMailMessage.class));
        assertEquals(503, assertThrows(ResponseStatusException.class,
                () -> service.requestEmail("member@example.test")).getStatusCode().value());
    }

    @Test
    void invalidInputDoesNotChangePassword() {
        assertThrows(ResponseStatusException.class, () -> service.requestEmail("invalid"));
        assertThrows(ResponseStatusException.class, () -> service.resetPassword("invalid", "new-pass123"));
        assertThrows(ResponseStatusException.class, () -> service.resetPassword(token, "short"));
        assertThrows(ResponseStatusException.class, () -> service.resetPassword(token, "가".repeat(25)));
        verify(users, never()).save(any());
    }

    @Test
    void usedOrExpiredLinkDoesNotChangePassword() {
        when(tokens.findByTokenHash(anyString())).thenReturn(Optional.of(new PasswordResetToken(1L, "hash", LocalDateTime.now())));
        when(tokens.consume(eq(1L), anyString(), any())).thenReturn(0);
        assertThrows(ResponseStatusException.class, () -> service.resetPassword(token, "new-pass123"));
        verify(users, never()).save(any());
    }

    @Test
    void savesHashedPasswordAndRejectsReuse() {
        when(tokens.findByTokenHash(anyString())).thenReturn(Optional.of(new PasswordResetToken(1L, "hash", LocalDateTime.now())));
        when(tokens.consume(eq(1L), anyString(), any())).thenReturn(1, 0);
        service.resetPassword(token, "new-pass123");
        ArgumentCaptor<String> password = ArgumentCaptor.forClass(String.class);
        verify(user).setPassword(password.capture());
        assertTrue(new BCryptPasswordEncoder().matches("new-pass123", password.getValue()));
        verify(users).save(user);
        assertThrows(ResponseStatusException.class, () -> service.resetPassword(token, "other-pass123"));
        verify(users, times(1)).save(user);
    }
}
