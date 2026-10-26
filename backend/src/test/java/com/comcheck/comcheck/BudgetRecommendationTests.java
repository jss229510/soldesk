package com.comcheck.comcheck;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import java.lang.reflect.Proxy;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.data.domain.Pageable;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import com.comcheck.comcheck.domain.estimate.controller.EstimateController;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimate.service.EstimateService;
import com.comcheck.comcheck.global.exception.GlobalExceptionHandler;

// API 계약과 조회 건수 제한을 검증하며 실제 DB에는 연결하지 않는다.
class BudgetRecommendationTests {
    @Test
    void returnsOneEstimateAndCannotNavigateToCheaperPages() throws Exception {
        Fixture fixture = new Fixture(List.of(recommendation()));

        fixture.mvc.perform(get("/api/estimates/recommended/budget").param("budget", "5000000"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estimatedId").value(1))
                .andExpect(jsonPath("$.totalPrice").value(4_715_810))
                .andExpect(jsonPath("$.estimates").doesNotExist())
                .andExpect(jsonPath("$.totalPages").doesNotExist());

        // 예전 클라이언트가 page/size를 보내도 더 저렴한 다음 견적을 조회하지 않는다.
        fixture.mvc.perform(get("/api/estimates/recommended/budget")
                        .param("budget", "5000000").param("page", "1").param("size", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.estimatedId").value(1));

        assertEquals(2, fixture.calls);
        assertEquals(5_000_000L, fixture.budget);
    }

    @Test
    void noMatchingEstimateReturnsNoContentIncludingAtZeroBudget() throws Exception {
        Fixture fixture = new Fixture(List.of());

        for (String budget : List.of("0", "300000")) {
            fixture.mvc.perform(get("/api/estimates/recommended/budget").param("budget", budget))
                    .andExpect(status().isNoContent())
                    .andExpect(content().string(""));
        }
        assertEquals(2, fixture.calls);
        assertEquals(300_000L, fixture.budget);
    }

    @Test
    void invalidBudgetsAreRejectedBeforeQuerying() throws Exception {
        Fixture fixture = new Fixture(List.of());

        fixture.mvc.perform(get("/api/estimates/recommended/budget"))
                .andExpect(status().isBadRequest());
        fixture.mvc.perform(get("/api/estimates/recommended/budget").param("budget", "-1"))
                .andExpect(status().isBadRequest());
        fixture.mvc.perform(get("/api/estimates/recommended/budget").param("budget", "invalid"))
                .andExpect(status().isBadRequest());

        assertEquals(0, fixture.calls);
    }

    private static Estimate recommendation() {
        Estimate estimate = new Estimate(null, "Streaming high quality", "STREAMING", null);
        ReflectionTestUtils.setField(estimate, "estimatedId", 1L);
        ReflectionTestUtils.setField(estimate, "isRecommend", true);
        estimate.changeTotals(4_715_810L, null);
        return estimate;
    }

    private static class Fixture {
        final MockMvc mvc;
        int calls;
        Long budget;

        Fixture(List<Estimate> rows) {
            EstimateRepository repository = (EstimateRepository) Proxy.newProxyInstance(
                    EstimateRepository.class.getClassLoader(), new Class<?>[] { EstimateRepository.class },
                    (proxy, method, args) -> {
                        if (!method.getName().equals("findRecommendedWithinBudget")) {
                            throw new UnsupportedOperationException(method.getName());
                        }
                        calls++;
                        assertEquals(true, args[0]);
                        budget = (Long) args[1];
                        Pageable pageable = (Pageable) args[2];
                        assertEquals(0, pageable.getOffset());
                        assertEquals(1, pageable.getPageSize());
                        return rows;
                    });
            mvc = MockMvcBuilders.standaloneSetup(new EstimateController(new EstimateService(repository, null)))
                    .setControllerAdvice(new GlobalExceptionHandler())
                    .build();
        }
    }
}
