package com.comcheck.comcheck.domain.part.entity;

import jakarta.persistence.*;

@Entity
// 이 클래스가 JPA Entity임을 나타냄
// DB의 PARTS 테이블과 연결되어 데이터를 객체 형태로 다룰 수 있게 함

@Table(name = "PARTS")
// 이 Entity가 Oracle의 PARTS 테이블과 매핑됨

public class Part {

    @Id
    // PART_ID를 기본키(PK)로 지정

    @Column(name = "\"part_id\"")
    // Oracle의 실제 컬럼명 "part_id"와 연결

    private Long partId;

    @Column(name = "\"category\"")
    // 부품 종류를 저장하는 컬럼

    private String category;

    @Column(name = "\"brand\"")
    // 제조사 정보를 저장하는 컬럼

    private String brand;

    @Column(name = "\"part_name\"")
    // 부품 제품명을 저장하는 컬럼

    private String part_name;

    @Column(name = "\"price\"")
    // 부품 가격을 저장하는 컬럼

    private Long price;

    @Column(name = "\"is_discontinued\"")
    // 단종 여부(Y/N)를 저장하는 컬럼

    private String is_discontinued;

    @Column(name = "\"image_url\"")
    // 상품 이미지 주소를 저장하는 컬럼

    private String image_url;

    @Column(name = "\"product_url\"")
    // 다나와 상품 페이지 주소를 저장하는 컬럼

    private String product_url;


    // DB에서 조회한 필드 값을 외부에서 읽을 수 있도록 Getter 제공

    public Long getPartId() {
        return partId;
    }

    public String getCategory() {
        return category;
    }

    public String getBrand() {
        return brand;
    }

    public String getPartName() {
        return part_name;
    }

    public Long getPrice() {
        return price;
    }

    public String getIsDiscontinued() {
        return is_discontinued;
    }

    public String getImageUrl() {
        return image_url;
    }

    public String getProductUrl() {
        return product_url;
    }
}