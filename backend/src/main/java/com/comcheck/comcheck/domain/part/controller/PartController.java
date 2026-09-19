package com.comcheck.comcheck.domain.part.controller;

import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.part.service.PartService;
import com.comcheck.comcheck.domain.partspec.service.PartSpecService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/parts")
public class PartController {

    private final PartSpecService partSpecService;
    private final PartService partService;

    public PartController(PartService partService, PartSpecService partSpecService) {
        this.partService = partService;
        this.partSpecService = partSpecService;
    }

    // 전체 부품 조회
    @GetMapping
    public List<Part> getParts(
            @RequestParam(required = false) String category) {
        if (category != null && !category.isBlank()) {
            return partService.getPartsByCategory(category);
        }

        return partService.getAllParts();
    }

    // 부품 한 개 조회
    @GetMapping("/{partId}")
    public Part getPartById(@PathVariable Long partId) {
        return partService.getPartById(partId);
    }

}