package com.comcheck.comcheck.domain.part.controller;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.service.PartService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/parts")
public class PartController {

    private final PartService partService;

    public PartController(PartService partService) {
        this.partService = partService;
    }

    // 전체 부품 조회
    @GetMapping
    public List<Part> getAllParts() {
        return partService.getAllParts();
    }

    // 부품 한 개 조회
    @GetMapping("/{partId}")
    public Part getPartById(@PathVariable Long partId) {
        return partService.getPartById(partId);
    }
}