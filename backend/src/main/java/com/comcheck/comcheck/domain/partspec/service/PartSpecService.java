package com.comcheck.comcheck.domain.partspec.service;

import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.partspec.entity.PartSpec;
import com.comcheck.comcheck.domain.partspec.repository.PartSpecRepository;

import java.util.List;
import java.util.Optional;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록

public class PartSpecService {
    
    private final PartSpecRepository partSpecRepository;
    // Repository를 주입받아 DB에 접근할 수 있도록 함
    public PartSpecService(PartSpecRepository partSpecRepository){
        this.partSpecRepository = partSpecRepository;
    }

     // 특정 부품의 스펙 목록 조회
    // 스펙이 하나도 없으면 빈 리스트([])를 반환
    public List<PartSpec> getSpecsByPartId(Long partId) {
        return partSpecRepository.findByPartIdOrderBySpecIdAsc(partId);
    }
    // 기능 하나 조회
    public PartSpec getSpecById(Long specId){
        return partSpecRepository.findById(specId)
                .orElse(null);
    }

    // 특정 부품에 속한 스펙 하나 조회
    // 없거나 다른 부품의 스펙이면 Optional.empty() 반환 → Controller에서 404 처리
    public Optional<PartSpec> getSpecOfPart(Long partId, Long specId) {
        return partSpecRepository.findBySpecIdAndPartId(specId, partId);
    }


}   

