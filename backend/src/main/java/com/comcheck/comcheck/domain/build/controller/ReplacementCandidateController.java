package com.comcheck.comcheck.domain.build.controller;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.comcheck.comcheck.domain.build.ReplacementCandidateService;
import com.comcheck.comcheck.domain.build.dto.ReplacementCandidateResponse;
import com.comcheck.comcheck.domain.build.dto.ReplacementRequest;

import jakarta.validation.Valid;

@RestController 
@RequestMapping("/api/build")
public class ReplacementCandidateController {

    private final ReplacementCandidateService
            replacementCandidateService;

    public ReplacementCandidateController(
            ReplacementCandidateService
                    replacementCandidateService) {

        this.replacementCandidateService =
                replacementCandidateService;
        }

     @PostMapping("/replacements")
    public ResponseEntity<
            List<ReplacementCandidateResponse>> getCandidates(
                    @Valid @RequestBody
                    ReplacementRequest request) {

        return ResponseEntity.ok(
                replacementCandidateService
                        .getCandidates(request));
    }        
}