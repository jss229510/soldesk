package com.comcheck.comcheck.domain.cartitem.entity;

import com.comcheck.comcheck.domain.cart.entity.Cart;
import com.comcheck.comcheck.domain.part.entity.Part;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;

@Entity
@Table(name = "CART_ITEMS")
public class CartItem {

    @Id
    // 기본키(PK)로 지정
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "CART_ITEMS_SEQ_GENERATOR")
    // 값을 자동 생성하도록 설정 (시퀀스 방식)
    @SequenceGenerator(name = "CART_ITEMS_SEQ_GENERATOR", sequenceName = "CART_ITEMS_SEQ", allocationSize = 1)
    // 사용할 시퀀스 생성기 정의 (DB 시퀀스 이름, 한 번에 1개씩)

    @Column(name = "\"cart_item_id\"")
    // 실제 컬럼명 cart_item_id와 연결
    private Long cartItemId;

    @ManyToOne (fetch = FetchType.LAZY)
    // 품목 여러 개가 장바구니 하나에 속하는 관계 표시, 필요할 때 가져오도록 설정
    @JoinColumn (name = "\"cart_id\"", nullable = false)
    // FK 컬럼 cart_id와 연결, 비어 있으면 안 됨
    private Cart cart;

    @ManyToOne (fetch = FetchType.LAZY)
    @JoinColumn (name = "\"part_id\"", nullable = false)
    // FK 컬럼 part_id와 연결, 비어 있으면 안 됨
    private Part part;


    @Column (name = "\"quantity\"", nullable = false)
    // 실제 컬럼명 quantity와 연결, 비어 있으면 안 됨
    private Long quantity;

    
    // ===== added_at (장바구니에 담은 날짜) =====
    // 실제 컬럼명 added_at과 연결, 비어 있으면 안 되고 처음 저장 후 수정되면 안 됨
    // 필드 선언 (날짜+시간 타입)

    // ===== 생성자 =====
    // JPA가 사용하는 기본 생성자 (외부에서 함부로 못 쓰게 접근 제한)
    // 품목을 새로 만들 때 쓰는 생성자 (부품과 수량을 받아서 저장, 수량이 없으면 1개)

    // ===== 날짜 자동 처리 =====
    // DB에 처음 저장되기 직전에 실행: 담은 날짜를 현재 시간으로 채움

    // ===== 비즈니스 메서드 =====
    // 장바구니 연결: 이 품목이 속한 장바구니를 지정 (Cart의 품목 추가 메서드에서 호출)
    // 수량 변경: 1개 미만이면 에러를 던지고, 아니면 수량을 바꿈 (테이블의 CHECK 조건과 같은 역할)

    // ===== Getter =====
    // cartItemId, 장바구니, 부품, 수량, 담은 날짜를 읽을 수 있게 제공

}
