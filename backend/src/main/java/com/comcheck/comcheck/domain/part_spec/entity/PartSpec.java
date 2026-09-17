package com.comcheck.comcheck.domain.part_spec.entity;

import jakarta.persistence.*;

@Entity
// 이 클래스가 JPA Entity임을 나타냄
// DB의 PART_SPECS 테이블과 연결되어 데이터를 객체 형태로 다룰 수 있게 함

@Table(name = "PART_SPECS")
// 이 Entity가 Oracle의 PART_SPECS 테이블과 매핑됨

public class PartSpec {

    @Id
    // SPEC_ID를 기본키(PK)로 지정

    @Column(name = "\"spec_id\"")
    // Oracle의 실제 컬럼명 "spec_id"와 연결

    private Long specId;

    @Column(name = "\"part_id\"")
    // 어떤 부품의 스펙인지 가리키는 컬럼 (PARTS 테이블 참조)

    private Long partId;

    @Column(name = "\"spec_key\"")
    // 스펙 항목명을 저장하는 컬럼 (예: 코어 수, 클럭)

    private String specKey;

    @Column(name = "\"spec_value\"")
    // 스펙 값을 저장하는 컬럼 (예: 8, 3.6)

    private String specValue;

    @Column(name = "\"spec_unit\"")
    // 스펙 단위를 저장하는 컬럼 (예: GHz, GB)

    private String specUnit;


    // DB에서 조회한 필드 값을 외부에서 읽을 수 있도록 Getter 제공

    public Long getSpecId() {
        return specId;
    }

    public Long getPartId() {
        return partId;
    }

    public String getSpecKey() {
        return specKey;
    }

    public String getSpecValue() {
        return specValue;
    }

    public String getSpecUnit() {
        return specUnit;
    }
}