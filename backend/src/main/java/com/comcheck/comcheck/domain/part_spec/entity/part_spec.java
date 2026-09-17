package com.comcheck.comcheck.domain.part_spec.entity;
import jakarta.persistence.*;

@Entity 

@Table(name= "PART_SPECS")

public class part_spec{

    @Id
    // spec_id

    @Column(name = "\"spec_id\"")
    // Oracle의 실제 컬럼명 "spec_id"와 연결

    private Long specId;

     @Column(name = "\"part_id\"")
    // 어떤 부품의 스펙인지 가리키는 컬럼 
    
    private Long partId;

     @Column(name = "\"spec_key\"")
    // 스펙 항목명을 저장하는 컬럼

    private String specKey;

     @Column(name = "\"spec_value\"")
    // 스펙 값을 저장하는 컬럼 

    private String specValue;
 
    @Column(name = "\"spec_unit\"")
    // 스펙 단위를 저장하는 컬럼

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