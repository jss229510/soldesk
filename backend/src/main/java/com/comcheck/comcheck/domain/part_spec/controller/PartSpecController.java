package com.comcheck.comcheck.domain.part_spec.controller;

import com.comcheck.comcheck.domain.part_spec.entity.part_spec;
import com.comcheck.comcheck.domain.part_spec.service.PartSpecService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import org.springframework.web.bind.annotation.RequestParam;

@RestController 

@RequestMapping("/api/part-specs")


public class PartSpecController {
    
    private final PartSpecService partSpecService;

    public  PartSpecController(PartSpecService partSpecService){
        this.partSpecService = partSpecService;
    }

    @GetMapping 

    public List<part_spec> getAllSpecs(){

        return  partSpecService.getAllSpecs();
    }

    @GetMapping("/{specId}")
    public part_spec getSpecById(@PathVariable Long specId){
        return partSpecService.getSpecById(specId);
    }

}
