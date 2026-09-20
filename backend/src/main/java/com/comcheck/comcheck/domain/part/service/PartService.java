package com.comcheck.comcheck.domain.part.service;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.repository.PartRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록

public class PartService {

    private final PartRepository partRepository;

    // Repository를 주입받아 DB에 접근할 수 있도록 함
    public PartService(PartRepository partRepository) {
        this.partRepository = partRepository;
    }

    // PARTS 테이블의 모든 부품 정보를 조회
    public List<Part> getAllParts() {

        // Repository의 findAll()을 이용하여 전체 부품 조회
        return partRepository.findAll();
    }

    // 부품 하나 조회
    public Part getPartById(Long partId) {
        return partRepository.findById(partId)
                .orElse(null);
    }

    // 카테고리 별 부품 조회
    public List<Part> getPartsByCategory(String category) {
        return partRepository.findByCategory(category);
    }
}