package com.comcheck.comcheck.domain.part_spec.repository;

import com.comcheck.comcheck.domain.part_spec.entity.part_spec;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PartSpecRepository extends JpaRepository<part_spec, Long> {
    
}
