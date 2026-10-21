package com.comcheck.comcheck;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.Base64;
import java.util.List;
import java.util.Optional;

import jakarta.servlet.Filter;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockServletContext;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

import com.comcheck.comcheck.config.SecurityConfig;
import com.comcheck.comcheck.domain.estimate.dto.EstimateResponse;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimateitem.controller.EstimateItemController;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemCreateRequest;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemQuantityUpdateRequest;
import com.comcheck.comcheck.domain.estimateitem.dto.EstimateItemResponse;
import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.estimateitem.repository.EstimateItemRepository;
import com.comcheck.comcheck.domain.estimateitem.service.EstimateItemService;
import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.security.JwtAuthenticationFilter;
import com.comcheck.comcheck.domain.user.service.JwtTokenProvider;
import com.comcheck.comcheck.global.exception.GlobalExceptionHandler;
import com.comcheck.comcheck.global.exception.SecurityErrorResponseWriter;

// 권한 검사는 메모리 안의 견적으로 검증하며 실제 DB를 변경하지 않는다.
class BudgetEstimateTests {
    @Test
    void sharedEstimateHasNoOwnerAndCanBeConvertedToResponse() {
        Estimate shared = new Store().shared;
        EstimateResponse response = EstimateResponse.from(shared);
        assertNull(response.userId());
        assertNull(response.nickname());
        assertTrue(response.recommend());
        assertFalse(shared.isOwnedBy(null));
        assertFalse(shared.isOwnedBy(7L));
    }

    @Test
    void personalEstimateKeepsItsOwnerInTheResponse() {
        Estimate personal = new Store().personal;
        EstimateResponse response = EstimateResponse.from(personal);
        assertEquals(7L, response.userId());
        assertEquals("owner", response.nickname());
        assertTrue(personal.isOwnedBy(7L));
        assertFalse(personal.isOwnedBy(8L));
    }

    @Test
    void estimatePriceStaysAtTheSavedUnitPriceWhenMarketPriceChanges() {
        Store store = new Store();
        ReflectionTestUtils.setField(store.part, "price", 250_000L);
        store.sharedItem.changeQuantity(3L);
        EstimateItemResponse response = EstimateItemResponse.from(store.sharedItem);
        assertEquals(100_000L, response.unitPrice());
        assertEquals(300_000L, response.itemPrice());
    }

    @Test
    void sharedItemsAreReadableWithoutLogin() {
        var rows = new Store().service.getItems(null, 1L);
        assertEquals(1, rows.size());
        assertEquals(100_000L, rows.get(0).unitPrice());
    }

    @Test
    void personalItemsRequireLoginAndTheCorrectOwner() {
        Store store = new Store();
        assertStatus(HttpStatus.UNAUTHORIZED, () -> store.service.getItems(null, 2L));
        assertStatus(HttpStatus.FORBIDDEN, () -> store.service.getItems(8L, 2L));
        assertEquals(1, store.service.getItems(7L, 2L).size());
    }

    @Test
    void publicReadDoesNotGivePermissionToModifySharedItems() {
        Store store = new Store();
        assertStatus(HttpStatus.FORBIDDEN,
                () -> store.service.create(7L, 1L, new EstimateItemCreateRequest(10L, 1L)));
        assertStatus(HttpStatus.FORBIDDEN,
                () -> store.service.updateQuantity(7L, 1L, 11L, new EstimateItemQuantityUpdateRequest(2L)));
        assertStatus(HttpStatus.FORBIDDEN, () -> store.service.delete(7L, 1L, 11L));
    }

    @Test
    void securityAllowsSharedReadsAndEnforcesPrivateOwnership() throws Exception {
        try (var context = webContext()) {
            MockMvc mvc = mvc(context);
            mvc.perform(get("/api/estimates/1/items")).andExpect(status().isOk());
            mvc.perform(get("/api/estimates/2/items")).andExpect(status().isUnauthorized());
            var tokens = context.getBean(JwtTokenProvider.class);
            mvc.perform(get("/api/estimates/2/items")
                    .header("Authorization", "Bearer " + tokens.createToken(8L)))
                    .andExpect(status().isForbidden());
            mvc.perform(get("/api/estimates/2/items")
                    .header("Authorization", "Bearer " + tokens.createToken(7L)))
                    .andExpect(status().isOk());
        }
    }

    @Test
    void securityStillRejectsAnonymousWrites() throws Exception {
        try (var context = webContext()) {
            MockMvc mvc = mvc(context);
            mvc.perform(post("/api/estimates/1/items")
                    .contentType(MediaType.APPLICATION_JSON).content("{\"partId\":10,\"quantity\":1}"))
                    .andExpect(status().isUnauthorized());
            mvc.perform(patch("/api/estimates/1/items/11/quantity")
                    .contentType(MediaType.APPLICATION_JSON).content("{\"quantity\":2}"))
                    .andExpect(status().isUnauthorized());
            mvc.perform(delete("/api/estimates/1/items/11")).andExpect(status().isUnauthorized());
        }
    }

    private static void assertStatus(HttpStatus status, Runnable action) {
        assertEquals(status, assertThrows(ResponseStatusException.class, action::run).getStatusCode());
    }

    private static AnnotationConfigWebApplicationContext webContext() {
        var context = new AnnotationConfigWebApplicationContext();
        context.setServletContext(new MockServletContext());
        context.register(SecurityConfig.class, TestWebConfig.class);
        context.refresh();
        return context;
    }

    private static MockMvc mvc(AnnotationConfigWebApplicationContext context) {
        return MockMvcBuilders.webAppContextSetup(context)
                .addFilters(context.getBean("springSecurityFilterChain", Filter.class)).build();
    }

    @TestConfiguration(proxyBeanMethods = false)
    @EnableWebMvc
    static class TestWebConfig {
        @Bean EstimateItemController controller() { return new EstimateItemController(new Store().service); }
        @Bean GlobalExceptionHandler exceptionHandler() { return new GlobalExceptionHandler(); }
        @Bean SecurityErrorResponseWriter errorWriter() { return new SecurityErrorResponseWriter(); }
        @Bean JwtTokenProvider tokenProvider() {
            return new JwtTokenProvider(Base64.getEncoder().encodeToString(new byte[64]));
        }
        @Bean JwtAuthenticationFilter jwtFilter(JwtTokenProvider provider, SecurityErrorResponseWriter writer) {
            return new JwtAuthenticationFilter(provider, writer);
        }
    }

    private static <T> T repository(Class<T> type, InvocationHandler handler) {
        return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
    }

    private static class Store {
        final Part part = new Part();
        final Estimate shared = new Estimate(null, "Shared", "OFFICE", null);
        final Estimate personal;
        final EstimateItem sharedItem;
        final EstimateItem personalItem;
        final EstimateItemService service;

        Store() {
            User owner = new User("owner@example.com", "test-hash", "owner");
            ReflectionTestUtils.setField(owner, "userId", 7L);
            personal = new Estimate(owner, "Personal", "OFFICE", 500_000L);
            ReflectionTestUtils.setField(shared, "estimatedId", 1L);
            ReflectionTestUtils.setField(shared, "isRecommend", true);
            ReflectionTestUtils.setField(personal, "estimatedId", 2L);
            ReflectionTestUtils.setField(part, "partId", 10L);
            ReflectionTestUtils.setField(part, "price", 100_000L);
            sharedItem = new EstimateItem(shared, part, 1L);
            personalItem = new EstimateItem(personal, part, 1L);
            EstimateRepository estimates = repository(EstimateRepository.class, (proxy, method, args) -> {
                if (method.getName().equals("findById")) {
                    return args[0].equals(1L) ? Optional.of(shared)
                            : args[0].equals(2L) ? Optional.of(personal) : Optional.empty();
                }
                throw new UnsupportedOperationException(method.getName());
            });
            EstimateItemRepository items = repository(EstimateItemRepository.class, (proxy, method, args) -> {
                if (method.getName().equals("findByEstimate_EstimatedId")) {
                    return args[0].equals(1L) ? List.of(sharedItem) : List.of(personalItem);
                }
                throw new UnsupportedOperationException(method.getName());
            });
            PartRepository parts = repository(PartRepository.class, (proxy, method, args) -> {
                throw new UnsupportedOperationException(method.getName());
            });
            service = new EstimateItemService(items, estimates, parts);
        }
    }
}
