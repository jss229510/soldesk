package com.comcheck.comcheck.domain.partspec.dto;

public record PartSpecResponse(
    Long specId,
    Long partId,
    String specKey,
    String specValue,
    String specUnit
){

}
