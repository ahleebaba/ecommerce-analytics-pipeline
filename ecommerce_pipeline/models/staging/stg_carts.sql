{# carts exclude order details#}
WITH source AS (
    SELECT * FROM {{ source('ingest_ecommerce', 'carts') }}
),

unnested AS (
    SELECT
        -- Cart level fields
        id                                              AS cart_id,
        userId                                          AS customer_id,
        total                                           AS cart_total,
        discountedTotal                                 AS cart_discounted_total,
        totalProducts                                   AS total_products,
        totalQuantity                                   AS total_quantity,

        -- Airbyte metadata
        _airbyte_extracted_at                           AS ingested_at

    FROM source

)

SELECT * FROM unnested