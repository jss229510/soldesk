package com.comcheck.comcheck.domain.build;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "build.accessories.apply-date")
public class RecommendationAccessoryRunner implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(
            RecommendationAccessoryRunner.class);

    private final RecommendationAccessoryWriter writer;
    private final String dateCode;

    public RecommendationAccessoryRunner(
            RecommendationAccessoryWriter writer,
            @Value("${build.accessories.apply-date}") String dateCode) {

        this.writer = writer;
        this.dateCode = dateCode;
    }

    @Override
    public void run(ApplicationArguments args) {
        log.info("추천 견적 케이스·쿨러 반영 시작: 날짜 {}", dateCode);

        int processed = writer.applyDefaults(dateCode);

        log.info("추천 견적 케이스·쿨러 반영 완료: 날짜 {} / 견적 {}건",
                dateCode, processed);
    }
}
