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
import com.comcheck.comcheck.domain.estimate.controller.EstimateController;
import com.comcheck.comcheck.domain.estimate.dto.EstimatePartSpecRow;
import com.comcheck.comcheck.domain.estimate.dto.EstimatePowerCheckRequest;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimate.service.EstimateService;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import com.comcheck.comcheck.domain.user.security.JwtAuthenticationFilter;
import com.comcheck.comcheck.domain.user.service.JwtTokenProvider;
import com.comcheck.comcheck.global.exception.GlobalExceptionHandler;
import com.comcheck.comcheck.global.exception.SecurityErrorResponseWriter;

// Repository doubles only allow reads. An unexpected save/delete fails the test.
class DraftPowerCheckTests {
    private static final String VALID_BODY = "{\"items\":[{\"partId\":1,\"quantity\":1},{\"partId\":2,\"quantity\":1},{\"partId\":3,\"quantity\":1}]}";
    private static final List<EstimatePartSpecRow> COMPLETE_ROWS = List.of(
            row(1, "CPU", "tdp_watt", "100"),
            row(2, "GPU", "tdp_watt", "200"),
            row(2, "GPU", "recommended_psu_watt", "650"),
            row(3, "PSU", "wattage", "650"));

    @Test
    void draftAndExistingStoredEstimateKeepTheSamePowerRule() {
        EstimateService service = service(COMPLETE_ROWS);
        var stored = service.checkPower(1L, null);
        var draft = service.checkDraftPower(request(1, 2, 3));
        assertEquals("OK", stored.status());
        assertEquals(stored.status(), draft.status());
        assertEquals(stored.cpuTdp(), draft.cpuTdp());
        assertEquals(stored.gpuTdp(), draft.gpuTdp());
        assertEquals(stored.totalPower(), draft.totalPower());
        assertEquals(stored.requiredWattage(), draft.requiredWattage());
        assertEquals(stored.psuWattage(), draft.psuWattage());
        assertEquals(1L, stored.estimateId());
        assertNull(draft.estimateId());
    }

    @Test
    void insufficientPsuIsReported() {
        var response = service(List.of(row(1, "GPU", "recommended_psu_watt", "750"),
                row(2, "PSU", "wattage", "650"))).checkDraftPower(request(1, 2));
        assertEquals("INSUFFICIENT", response.status());
        assertFalse(response.compatible());
        assertEquals(750L, response.requiredWattage());
    }

    @Test
    void fallbackUsesRequestedQuantityAndThirtyPercentMargin() {
        EstimateService service = service(List.of(row(1, "CPU", "tdp_watt", "100"),
                row(2, "GPU", "tdp_watt", "200"), row(3, "PSU", "wattage", "650")));
        var response = service.checkDraftPower(new EstimatePowerCheckRequest(List.of(
                new EstimatePowerCheckRequest.Item(1L, 1L),
                new EstimatePowerCheckRequest.Item(2L, 2L),
                new EstimatePowerCheckRequest.Item(3L, 1L))));
        assertEquals(400L, response.gpuTdp());
        assertEquals(500L, response.totalPower());
        assertEquals(650L, response.requiredWattage());
        assertEquals("OK", response.status());
    }

    @Test
    void noGpuKeepsTheExistingFourHundredWattMinimum() {
        var response = service(List.of(row(1, "CPU", "tdp_watt", "65"),
                row(3, "PSU", "wattage", "399"))).checkDraftPower(request(1, 3));
        assertEquals(400L, response.requiredWattage());
        assertEquals("INSUFFICIENT", response.status());
    }

    @Test
    void absentPsuAndPsuWithMissingSpecsAreDifferent() {
        assertEquals("NO_PSU", service(List.of(row(1, "CPU", "tdp_watt", "65")))
                .checkDraftPower(request(1)).status());
        assertEquals("UNKNOWN", service(List.of(row(1, "CPU", "tdp_watt", "65"),
                row(3, "PSU", null, null))).checkDraftPower(request(1, 3)).status());
    }

    @Test
    void gpuWithoutPowerSpecsDoesNotGetMistakenForAnOfficeBuild() {
        var response = service(List.of(row(1, "CPU", "tdp_watt", "65"),
                row(2, "GPU", null, null), row(3, "PSU", "wattage", "650")))
                .checkDraftPower(request(1, 2, 3));
        assertEquals("UNKNOWN", response.status());
        assertNull(response.requiredWattage());
        assertFalse(response.compatible());
    }

    @Test
    void fallbackNeedsCpuAndGpuTdpWhenNoRecommendedPsuIsKnown() {
        var response = service(List.of(row(1, "CPU", null, null),
                row(2, "GPU", "tdp_watt", "200"), row(3, "PSU", "wattage", "650")))
                .checkDraftPower(request(1, 2, 3));
        assertEquals("UNKNOWN", response.status());
    }

    @Test
    void duplicateUnknownAndInvalidPartsAreRejected() {
        EstimateService service = service(COMPLETE_ROWS);
        for (var request : List.of(request(1, 1), request(1, 99), request(),
                new EstimatePowerCheckRequest(List.of(new EstimatePowerCheckRequest.Item(1L, 0L))))) {
            var error = assertThrows(ResponseStatusException.class, () -> service.checkDraftPower(request));
            assertEquals(HttpStatus.BAD_REQUEST, error.getStatusCode());
        }
    }

    @Test
    void newPublicPostDoesNotOpenExistingEstimateOrPaymentWrites() throws Exception {
        try (var context = webContext()) {
            MockMvc mvc = mvc(context);
            mvc.perform(post("/api/estimates/power-check").contentType(MediaType.APPLICATION_JSON).content(VALID_BODY))
                    .andExpect(status().isOk());
            mvc.perform(get("/api/estimates/1/power-check")).andExpect(status().isOk());
            for (String path : List.of("/api/estimates", "/api/estimates/1/items", "/api/payments/ready", "/api/boards")) {
                mvc.perform(post(path).contentType(MediaType.APPLICATION_JSON).content("{}"))
                        .andExpect(status().isUnauthorized());
            }
        }
    }

    @Test
    void controllerValidatesNestedPartIdsQuantitiesAndRequestSize() throws Exception {
        try (var context = webContext()) {
            MockMvc mvc = mvc(context);
            for (String body : List.of("{}", "{\"items\":[]}", "{\"items\":[null]}",
                    "{\"items\":[{\"partId\":0,\"quantity\":1}]}",
                    "{\"items\":[{\"partId\":1.5,\"quantity\":1}]}",
                    "{\"items\":[{\"partId\":1,\"quantity\":101}]}",
                    "{\"items\":[{\"partId\":1,\"quantity\":1.5}]}")) {
                mvc.perform(post("/api/estimates/power-check").contentType(MediaType.APPLICATION_JSON).content(body))
                        .andExpect(status().isBadRequest());
            }
            String tooMany = "{\"items\":[" + String.join(",", java.util.Collections.nCopies(17,
                    "{\"partId\":1,\"quantity\":1}")) + "]}";
            mvc.perform(post("/api/estimates/power-check").contentType(MediaType.APPLICATION_JSON).content(tooMany))
                    .andExpect(status().isBadRequest());
        }
    }

    private static EstimatePartSpecRow row(long id, String category, String key, String value) {
        return new EstimatePartSpecRow(id, category, key, value, 1L);
    }

    private static EstimatePowerCheckRequest request(long... ids) {
        return new EstimatePowerCheckRequest(java.util.Arrays.stream(ids)
                .mapToObj(id -> new EstimatePowerCheckRequest.Item(id, 1L)).toList());
    }

    private static EstimateService service(List<EstimatePartSpecRow> rows) {
        Estimate shared = new Estimate(null, "Shared", "OFFICE", null);
        ReflectionTestUtils.setField(shared, "estimatedId", 1L);
        ReflectionTestUtils.setField(shared, "isRecommend", true);
        EstimateRepository estimates = proxy(EstimateRepository.class, (object, method, args) -> switch (method.getName()) {
            case "findPowerSpecsByPartIds" -> rows.stream().filter(row -> ((List<?>) args[0]).contains(row.partId())).toList();
            case "findPowerSpecs" -> rows;
            case "findById" -> Optional.of(shared);
            default -> throw new AssertionError("Unexpected repository operation: " + method.getName());
        });
        UserRepository users = proxy(UserRepository.class, (object, method, args) -> {
            throw new AssertionError("Unexpected user operation: " + method.getName());
        });
        return new EstimateService(estimates, users);
    }

    private static <T> T proxy(Class<T> type, InvocationHandler handler) {
        return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
    }

    private static AnnotationConfigWebApplicationContext webContext() {
        var context = new AnnotationConfigWebApplicationContext();
        context.setServletContext(new MockServletContext());
        context.register(SecurityConfig.class, WebConfig.class);
        context.refresh();
        return context;
    }

    private static MockMvc mvc(AnnotationConfigWebApplicationContext context) {
        return MockMvcBuilders.webAppContextSetup(context)
                .addFilters(context.getBean("springSecurityFilterChain", Filter.class)).build();
    }

    @TestConfiguration(proxyBeanMethods = false)
    @EnableWebMvc
    static class WebConfig {
        @Bean EstimateController controller() { return new EstimateController(service(COMPLETE_ROWS)); }
        @Bean GlobalExceptionHandler exceptionHandler() { return new GlobalExceptionHandler(); }
        @Bean SecurityErrorResponseWriter errorWriter() { return new SecurityErrorResponseWriter(); }
        @Bean JwtTokenProvider tokenProvider() {
            return new JwtTokenProvider(Base64.getEncoder().encodeToString(new byte[64]));
        }
        @Bean JwtAuthenticationFilter jwtFilter(JwtTokenProvider provider, SecurityErrorResponseWriter writer) {
            return new JwtAuthenticationFilter(provider, writer);
        }
    }
}
