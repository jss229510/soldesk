# insertCoolerAndCase.py

def cooler_end_case():
    return [
        {# 수냉쿨러(가성비)
            "part": {
               "category": "COOLER",
                "brand": "darkFlash",
                "part_name": "darkFlash NEBULA DN-360D ARGB (화이트)",
                "price": 95810,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/734/377/064/be8bce4ba48f4b7a8c254429a2a0fb2f.jpeg?shrink=330:*&_v=20261020084428",
                "product_url": "https://prod.danawa.com/info/?pcode=64377734&cate=11336856",
            },
            
            "specs": [
                {
                    "spec_key": "cpu_socket",
                    "spec_value": ["LGA1700","LGA1200","LGA115x"],
                    "spec_unit" : None,
                },
                {
                    "spec_key": "radiator_length",
                    "spec_value": 397,
                    "spec_unit": "mm",
                },
                {
                    "spec_key": "cooler_type",
                    "spec_value": ["수냉"],
                    "spec_unit": None,
                },
            ]
        },
        
        {# 수냉쿨러(순정)
            "part": {
                "category": "COOLER",
                "brand": "ARCTIC",
                "part_name": "ARCTIC Liquid Freezer III PRO 360 서린",
                "price": 158480,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/246/045/092/d27fc1da2bfb4a4dafcf244079d49417.jpg?shrink=330:*&_v=20261020104003",
                "product_url": "https://prod.danawa.com/info/?pcode=92045246&cate=11336856",                
            },
            
            "specs": [
                {
                    "spec_key": "cpu_socket",
                    "spec_value": ["LGA1851","LGA1700","LGA1200","LGA115x","AM5","AM4"],
                    "spec_unit" : None,
                },
                {
                    "spec_key": "radiator_length",
                    "spec_value": 398,
                    "spec_unit": "mm",
                },
                {
                    "spec_key": "cooler_type",
                    "spec_value": ["수냉"],
                    "spec_unit": None,
                },
            ]
        },
        
        {# 공냉쿨러(듀얼타워)
            "part": {
                "category": "COOLER",
                "brand": "타무즈",
                "part_name": "타무즈 T880-V4D (블랙)",
                "price": 56190,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/297/108/092/35160a585b744a4081e2e09adc420c7e.jpg?shrink=330:*&_v=20261020083748",
                "product_url": "https://prod.danawa.com/info/?pcode=92108297&cate=11336857",                
            },
            
            "specs": [
                {
                    "spec_key": "cpu_socket",
                    "spec_value": ["LGA1851","LGA1700","LGA1200","LGA115x","LGA1366","LGA2011","LGA2066","AM5","AM4"],
                    "spec_unit" : None,
                },
                {
                    "spec_key": "warranty_height",
                    "spec_value": 154,
                    "spec_unit": "mm",
                },
                {
                    "spec_key": "cooler_type",
                    "spec_value": ["공냉"],
                    "spec_unit": None,
                },
            ]            
        },
        
        {# 공냉쿨러(싱글타워)
            "part": {
                "category": "COOLER",
                "brand": "DEEPCOOL",
                "part_name": "DEEPCOOL AG400 G2 (블랙)",
                "price": 21640,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/347/047/106/716ba88a085542d1a1e93c62a9fcf88f.jpeg?shrink=330:*&_v=20261020091518",
                "product_url": "https://prod.danawa.com/info/?pcode=106047347&cate=11336857",                
            },
            
            "specs": [
                {
                    "spec_key": "cpu_socket",
                    "spec_value": ["LGA1851","LGA1700","AM5","AM4"],
                    "spec_unit" : None,
                },
                {
                    "spec_key": "warranty_height",
                    "spec_value": 154.5,
                    "spec_unit": "mm",
                },
                {
                    "spec_key": "cooler_type",
                    "spec_value": ["공냉"],
                    "spec_unit": None,
                },
            ]            
        },
        
        {# 빅타워-메쉬(사무)
            "part":{
                "category": "CASE",
                "brand": "3RSYS",
                "part_name": "3RSYS T2000 Quiet (블랙)",
                "price": 130000,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/654/045/092/6f474407f1a04ec6b720a281b0247134.jpg?shrink=330:*&_v=20261020084448",
                "product_url": "https://prod.danawa.com/info/?pcode=92045654&cate=112775",
            },
            
            "specs":[
                {
                    "spec_key": "motherboad_support",
                    "spec_value": ["E-ATX","ATX","M-ATX","ITX"],
                    "spec_unit": None,
                },
                
                {
                    "spec_key": "max_gpu_length",
                    "spec_value": 420,
                    "spec_unit": "mm",
                },
                
                {
                    "spec_key": "max_cpu_length",
                    "spec_value": 180,
                    "spec_unit": "mm",
                },
            ]
        },
        {# 빅타워-어항(게이밍)
            "part":{
                "category": "CASE",
                "brand": "마이크로닉스",
                "part_name": "마이크로닉스 WIZMAX 우드리안 MAX",
                "price": 84310,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/156/559/079/07307f196d2644dcaf221c62354b5eaf.jpg?shrink=330:*&_v=20261020083613",
                "product_url": "https://prod.danawa.com/info/?pcode=79559156&cate=112775",
            },
            
            "specs":[
                {
                    "spec_key": "motherboad_support",
                    "spec_value": ["E-ATX","ATX","M-ATX","M-ITX"],
                    "spec_unit": None,
                },
                
                {
                    "spec_key": "max_gpu_length",
                    "spec_value": 410,
                    "spec_unit": "mm",
                },
                
                {
                    "spec_key": "max_cpu_length",
                    "spec_value": 160,
                    "spec_unit": "mm",
                },
            ]
        },
        
        {# 미들타워-어항(게이밍)
            "part":{
                "category": "CASE",
                "brand": "DAVEN",
                "part_name": "DAVEN D7 Mesh 세븐팬 ARGB PWM (블랙)",
                "price": 66780,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/069/076/124/4d13d3fc6576411f8ea9e861ab3ec10c.jpeg?shrink=330:*&_v=20261020091503",
                "product_url": "https://prod.danawa.com/info/?pcode=124076069&cate=112775",
            },
            
            "specs":[
                {
                    "spec_key": "motherboad_support",
                    "spec_value": ["E-ATX","ATX","M-ATX","ITX"],
                    "spec_unit": None,
                },
                
                {
                    "spec_key": "max_gpu_length",
                    "spec_value": 400,
                    "spec_unit": "mm",
                },
                
                {
                    "spec_key": "max_cpu_length",
                    "spec_value": 170,
                    "spec_unit": "mm",
                },
            ]
        },
        
        {# 미들타워-메쉬(사무)
            "part":{
                "category": "CASE",
                "brand": "오쓰",
                "part_name": "오쓰 SOLID FULL MESH (블랙)",
                "price": 63530,
                "is_discontinued": "N",
                "image_url": "https://img.danuri.io/catalog-image/968/694/122/e615d9bd3a46467d800b851f7784adbd.jpeg?shrink=330:*&_v=20261020080447",
                "product_url": "https://prod.danawa.com/info/?pcode=122694968&cate=112775",
            },
            
            "specs":[
                {
                    "spec_key": "motherboad_support",
                    "spec_value": ["E-ATX","ATX","M-ATX","ITX"],
                    "spec_unit": None,
                },
                
                {
                    "spec_key": "max_gpu_length",
                    "spec_value": 400,
                    "spec_unit": "mm",
                },
                
                {
                    "spec_key": "max_cpu_length",
                    "spec_value": 175,
                    "spec_unit": "mm",
                },
            ]
        },
    ]