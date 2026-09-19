package com.comcheck.comcheck.domain.partspec.controller;
 
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
 
import com.comcheck.comcheck.domain.partspec.entity.PartSpec;
import com.comcheck.comcheck.domain.partspec.service.PartSpecService;
 
import java.util.List;

@RestController
// HTTP 요청을 처리하고 결과를 JSON 형태로 반환하는 Controller
@RequestMapping("/api/parts/{partId}/specs")
// 스펙은 특정 부품(Part)에 종속된 데이터이므로 Part 하위 경로로 설정


public class PartSpecController {

    private final PartSpecService partSpecService;

    // Service를 주입받아 데이터를 가져올 수 있도록 함
    public PartSpecController(PartSpecService partSpecService) {
        this.partSpecService = partSpecService;
    }

    @GetMapping
    // GET /api/parts/{partId}/specs
    // 선택한 부품 하나의 스펙 목록만 반환
    public List<PartSpec> getSpecsByPartId(@PathVariable Long partId) {
        return partSpecService.getSpecsByPartId(partId);
    }

    @GetMapping("/{specId}")
    // 해당 부품의 스펙이 아니거나 존재하지 않으면 404 Not Found
    public ResponseEntity<PartSpec> getSpec(@PathVariable Long partId,
                                            @PathVariable Long specId) {
        return partSpecService.getSpecOfPart(partId, specId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }


}
