package com.comcheck.comcheck.domain.estimate.repository;


import org.springframework.data.jpa.repository.JpaRepository;

import com.comcheck.comcheck.domain.estimate.entity.Estimate;

import java.util.List;

public interface EstimateRepository extends JpaRepository<Estimate, Long>  {
    
}
