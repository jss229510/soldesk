package com.comcheck.comcheck.domain.partspec.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.comcheck.comcheck.domain.partspec.entity.PartSpec;
import com.comcheck.comcheck.domain.partspec.service.PartSpecService;

import java.util.List;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
// HTTP 요청을 처리하고 결과를 JSON 형태로 반환하는 Controller
@RequestMapping("/api/part_specs")
// 이 Controller의 기본 URL을 /api/part-specs로 설정

public class PartSpecController {

    private final PartSpecService partSpecService;

    // Service를 주입받아 데이터를 가져올 수 있도록 함
    public PartSpecController(PartSpecService partSpecService) {
        this.partSpecService = partSpecService;
    }

    @GetMapping
    // GET /api/parts 요청을 처리

    public List<PartSpec> getAllSpecs() {

        // Service를 호출하여 PART_SPECS 테이블의 전체 정보를 가져옴
        return partSpecService.getAllSpecs();
    }

    // 기능 하나 조회
    @GetMapping("/{specId}")
    public PartSpec getSpecById(@PathVariable Long specId) {
        return partSpecService.getSpecById(specId);
    }

}
