package com.comcheck.comcheck.domain.part_spec.service;

import com.comcheck.comcheck.domain.part_spec.entity.part_spec;
import com.comcheck.comcheck.domain.part_spec.repository.PartSpecRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록

public class PartSpecService {
    
    private final PartSpecRepository partSpecRepository;
    // Repository를 주입받아 DB에 접근할 수 있도록 함
    public PartSpecService(PartSpecRepository partSpecRepository){
        this.partSpecRepository = partSpecRepository;
    }

    //PART_SPECS 테이블의 모든 정보를 조회
    public List<part_spec> getAllSpecs(){
        
        // Repository의 findAll()을 이용하여 전체 부품 조회
        return partSpecRepository.findAll();
    }

    // 기능 하나 조회
    public part_spec getSpecById(Long specId){
        return partSpecRepository.findById(specId)
                .orElse(null);
    }


}   

