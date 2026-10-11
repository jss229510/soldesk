package com.comcheck.comcheck.domain.pricehistory.dto;

import java.time.LocalDate;

public record PriceHistoryResponse (

    Long id,
    Long price,
    LocalDate recordAt,
    String source
){
}