package com.comcheck.comcheck.domain.part.controller;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.service.PartService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
// HTTP 요청을 처리하고 결과를 JSON 형태로 반환하는 Controller

@RequestMapping("/api/parts")
// 이 Controller의 기본 URL을 /api/parts로 설정

public class PartController {

    private final PartService partService;

    // Service를 주입받아 부품 데이터를 가져올 수 있도록 함
    public PartController(PartService partService) {
        this.partService = partService;
    }

    @GetMapping
    // GET /api/parts 요청을 처리

    public List<Part> getAllParts() {

        // Service를 호출하여 PARTS 테이블의 전체 부품 정보를 가져옴
        return partService.getAllParts();
    }
}