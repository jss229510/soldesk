package com.comcheck.comcheck.domain.partspec.service;

import org.springframework.stereotype.Service;

import com.comcheck.comcheck.domain.partspec.dto.PartSpecResponse;
import com.comcheck.comcheck.domain.partspec.entity.PartSpec;
import com.comcheck.comcheck.domain.partspec.exception.PartSpecNotFoundException;
import com.comcheck.comcheck.domain.partspec.repository.PartSpecRepository;

import java.util.List;

@Service
// 이 클래스를 Spring의 Service 계층으로 등록

public class PartSpecService {

    private final PartSpecRepository partSpecRepository;

    // Repository를 주입받아 DB에 접근할 수 있도록 함
    public PartSpecService(PartSpecRepository partSpecRepository) {
        this.partSpecRepository = partSpecRepository;
    }

    // 특정 부품의 스펙 목록 조회
    // 스펙이 하나도 없으면 빈 리스트([])를 반환
    public List<PartSpecResponse> getSpecResponsesByPartId(Long partId) {
        return partSpecRepository.findByPartIdOrderBySpecIdAsc(partId)
                .stream()
                .map(this::toPartSpecResponse)
                .toList();
    }

    // 특정 부품에 속한 스펙 하나를 DTO로 반환한다.
    // 스펙이 없거나 다른 부품의 스펙이면 PartSpecNotFoundException을 발생시킨다.
    public PartSpecResponse getSpecResponseOfPart(Long partId, Long specId) {
        PartSpec partSpec = partSpecRepository.findBySpecIdAndPartId(specId, partId)
                .orElseThrow(() -> new PartSpecNotFoundException(partId, specId));
        return toPartSpecResponse(partSpec);
    }

    // Entity를 API 응답 모양으로 변환하는 공통 메서드
    private PartSpecResponse toPartSpecResponse(PartSpec partSpec) {
        return new PartSpecResponse(
                partSpec.getSpecId(),
                partSpec.getPartId(),
                partSpec.getSpecKey(),
                partSpec.getSpecValue(),
                partSpec.getSpecUnit());
    }

}
