package com.comcheck.comcheck.domain.part_spec.service;

import com.comcheck.comcheck.domain.part_spec.entity.part_spec;
import com.comcheck.comcheck.domain.part_spec.repository.PartSpecRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service

public class PartSpecService {
    
    private final PartSpecRepository partSpecRepository;

    public  PartSpecService(PartSpecRepository partSpecRepository){
        this.partSpecRepository = partSpecRepository;
    }

    //PART_SPECS 테이블의 모든 부품 정보를 조회
    public List<part_spec> getAllSpecs(){

        return partSpecRepository.findAll();
    }

    public part_spec getSpecById(Long specId){
        return partSpecRepository.findById(specId)
                .orElse(null);
    }


}   

