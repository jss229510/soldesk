package com.comcheck.comcheck.domain.part.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "PARTS")

public class Part {
    @Id
    @Column(name = "PART_ID")
    private Long partId;
    @Column(name = "CATEGORY")
    private String category;
    @Column(name = "BRAND")
    private String brand;
    @Column(name = "PART_NAME")
    private String part_name;
    @Column(name = "PRICE")
    private Long price;
    @Column(name = "IS_DISCONTINUED")
    private String is_discontinued;
    @Column(name = "IMAGE_URL")
    private String image_url;
    @Column(name = "PRODUCT_URL")
    private String product_url;

    public Long getPartId() {
        return partId;
    }

    public String getCategory() {
        return category;
    }

    public String getBrand() {
        return brand;
    }

    public String getPartName() {
        return part_name;
    }

    public Long getPrice() {
        return price;
    }

    public String getIsDiscontinued() {
        return is_discontinued;
    }

    public String getImageUrl() {
        return image_url;
    }

    public String getProductUrl() {
        return product_url;
    }
}
