package com.comcheck.comcheck.config;

import org.springframework.beans.factory.config.ConfigurableBeanFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;
import org.springframework.web.client.RestClient;

@Configuration(proxyBeanMethods = false)
public class RestClientConfig {

    // KakaoPayClient 생성자에 주입할 HTTP 클라이언트 빌더를 등록한다.
    // 각 주입마다 새 빌더를 만들어 인증 헤더 등의 설정이 다른 클라이언트와 섞이지 않게 한다.
    @Bean
    @Scope(ConfigurableBeanFactory.SCOPE_PROTOTYPE)
    public RestClient.Builder restClientBuilder() {
        return RestClient.builder();
    }
}
