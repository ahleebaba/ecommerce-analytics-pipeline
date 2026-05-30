WITH source AS (
    SELECT * FROM {{ source('ingest_ecommerce', 'products') }}
),

renamed AS (
    SELECT
        -- Primary key
        id                                          AS product_id,

        -- Product details
        title                                       AS product_name,
        description                                 AS product_description,
        category                                    AS product_category,
        brand                                       AS brand,
        sku                                         AS sku,
        tags                                        AS tags,
        JSON_VALUE(meta, '$.createdAt')             AS product_created_at,
        JSON_VALUE(meta, '$.updatedAt')             AS product_updated_at,

        -- Pricing
        price                                       AS price,
        discountPercentage                          AS discount_pct,

        -- Physical attributes
        weight                                      AS weight,
        JSON_VALUE(dimensions, '$.width')           AS dimension_width,
        JSON_VALUE(dimensions, '$.height')          AS dimension_height,
        JSON_VALUE(dimensions, '$.depth')           AS dimension_depth,

        -- Inventory & availability
        stock                                       AS stock_quantity,
        minimumOrderQuantity                        AS minimum_order_quantity,
        availabilityStatus                          AS availability_status,

        -- Ratings
        rating                                      AS rating,

        -- Policies
        returnPolicy                                AS return_policy,
        shippingInformation                         AS shipping_information,
        warrantyInformation                         AS warranty_information,

        -- Media
        thumbnail                                   AS thumbnail_url,

        -- Airbyte metadata
        _airbyte_extracted_at                       AS ingested_at

    FROM source
)

SELECT * FROM renamed