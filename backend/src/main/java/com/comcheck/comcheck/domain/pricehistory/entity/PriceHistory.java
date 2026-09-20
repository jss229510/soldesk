package com.comcheck.comcheck.domain.pricehistory.entity;

import java.time.LocalDate;

import jakarta.persistence.*;

@Entity
// 이 클래스가 JPA Entity임을 나타냄
// DB의 PARTS 테이블과 연결되어 데이터를 객체 형태로 다룰 수 있게 함

@Table(name = "PRICE_HISTORY")
// 이 Entity가 Oracle의 PARTS 테이블과 매핑됨

public class PriceHistory {

    @Id
    // PART_ID를 기본키(PK)로 지정

    @Column(name = "\"price_history_id\"")
    // Oracle의 실제 컬럼명 "part_id"와 연결

    private Long priceHistoryId;

    @Column(name = "\"part_id\"")
    // 부품 종류를 저장하는 컬럼

    private Long partId;

    @Column(name = "\"price\"")
    // 제조사 정보를 저장하는 컬럼

    private Long price;

    @Column(name = "\"recorded_at\"")
    // 부품 제품명을 저장하는 컬럼

    private LocalDate recordedAt;

    @Column(name = "\"source\"")
    // 부품 가격을 저장하는 컬럼

    private String source;

    // DB에서 조회한 필드 값을 외부에서 읽을 수 있도록 Getter 제공

    public Long getPartId() {
        return partId;
    }

    public Long getPriceHistoryId() {
        return priceHistoryId;
    }

    public LocalDate getRecordedAt() {
        return recordedAt;
    }

    public Long getPrice() {
        return price;
    }

    public String getSource() {
        return source;
    }
}